import logging
import queue
import can
import asyncio

from bs4 import BeautifulSoup
from typing import List, Any
from random import randint
from collections import Counter

from additional_scripts import logger_setup
from additional_scripts.analysis_utils import AnalysisUtils
from additional_scripts.analysis import Analysis
from hardware_control.multiplexer_config import MPconfig
from can_communication.socketcan_reader import READSocketcan
from cic_control.power_config import power_signal
from can_communication.socketcan_config import can_config


class CANWrapper(MPconfig, READSocketcan):

    def __init__(self):

        READSocketcan.__init__(self)
        MPconfig.__init__(self)
        self.cnt = Counter()
        self.error_counter = 0

        self.logger = logging.getLogger('mopshub_log.can_wrapper')

        can_config.can_setup(channel=0)
        can_config.can_setup(channel=1)
        can_config.start()
        self.start()
        can.util.set_logging_level('warning')

    async def read_sdo_can(self, node_id=None, index=None, subindex=None, channel=None, timeout=2000, max_data_bytes=8,
                           sdo_tx=0x600, sdo_rx=0x580):
        """Read an object via |SDO|
        Currently expedited and segmented transfer is supported by this method.
        The function will writing the dictionary request from the master to the node then read the response from
        the node to the master
        The user has to decide how to decode the data.
        """
        self.logger.info('Reading an object via |SDO|')
        if node_id is None or index is None or subindex is None or channel is None:
            self.logger.warning('SDO read protocol cancelled before it could begin.')
            return None

        self.cnt['SDO read total'] += 1
        self.logger.info(f'Send SDO read request to node {node_id}')

        cobid = sdo_tx + node_id
        msg = [0 for _ in range(max_data_bytes)]
        msg[0] = 0x40
        msg[1], msg[2] = index.to_bytes(2, 'little')
        msg[3] = subindex

        can_config.sem_config_block.acquire()
        self.logger.info("Start Communication")
        try:
            await self.write_can_message(channel, cobid, msg, timeout=timeout)
            self.current_subindex = subindex
            self.current_channel = channel
            self.cobid_ret = sdo_rx + node_id
        except can.CanError as e:
            self.logger.exception(e)
            self.cnt['SDO read request timeout'] += 1
            return None

        can_config.sem_recv_block.release()
        self.logger.info("Send Thread is waiting for receive thread to finish socket read")
        # Wait for can-message
        can_config.sem_read_block.acquire()
        self.logger.info("Receiving is finished. Processing received data")
        can_config.sem_config_block.release()
        self.logger.info("Communication finished")
        # Process can-messages
        message_valid = False
        error_response = False
        while not self.receive_queue.empty():
            frame = self.receive_queue.get()
            if frame is not None:
                cobid_ret, ret, dlc, flag, t, error_frame = (frame.arbitration_id, frame.data,
                                                             frame.dlc, frame.is_extended_id,
                                                             frame.timestamp, frame.is_error_frame)
                message_valid = (dlc == max_data_bytes
                                 and cobid_ret == sdo_rx + node_id
                                 and ret[0] in [0x80, 0x43, 0x47, 0x4b, 0x4f, 0x42]
                                 and int.from_bytes([ret[1], ret[2]], 'little') == index
                                 and ret[3] == subindex)
                error_response = (dlc == 8 and cobid_ret == 0x88 and ret[0] in [0x00])
            if error_response:
                self.error_counter += 1
                return None
            if message_valid:
                self.logger.info(f'We received a msg: {frame}')
                break
        else:
            self.logger.info('SDO read response timeout.')
            self.logger.info(f'NodeID: {node_id}')
            self.logger.info(f'Index: {index}')
            self.logger.info(f'Subindex: {subindex}')
            self.cnt['SDO read response timeout'] += 1
            return None

        # Check command byte
        if ret[0] == 0x80:
            abort_code = int.from_bytes(ret[4:], 'little')
            self.logger.error('Received SDO abort message while reading')
            self.logger.error(f'Object: {index}')
            self.logger.error(f'Subindex: {subindex}')
            self.logger.error(f'NodeID: {node_id}')
            self.logger.error(f'Abort code: {abort_code}')
            self.cnt['SDO read abort'] += 1
            return None

        n_data_bytes = 4 - ((ret[0] >> 2) & 0b11) if ret[0] != 0x42 else 4
        data = []
        for i in range(n_data_bytes):
            data.append(ret[4 + i])
        self.logger.info('Got data %s', data)

        return int.from_bytes(data, 'little')
        # return cobid_ret, int.from_bytes(data, 'little')

    async def read_adc_channels(self, file, directory, node_id, mp_channel, can_channel):
        """Start actual CANopen communication
        This function contains an endless loop in which it is looped over all
        ADC channels. Each value is read using
        :meth:`read_sdo_can` and written to its corresponding
        """
        # Setting Multiplexer
        try:
            self.mp_switch(mp_channel, can_channel)
            self.logger.info(f'MP Channel was set to {mp_channel} for can channel to {can_channel}')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'MP channel {mp_channel} could not be set')
            return None

        # Check power status
        try:
        # status = [status, locked_by_sys, locked_by_user]
            status = power_signal.check_status(mp_channel)
            if status[0] == 0 and bool(status[2]) is False and bool(status[1] is False):
                self.logger.error(f'Power is not enabled on Channel {mp_channel}')
                power_signal.power_on(mp_channel)
                self.logger.info(f'Power for channel {mp_channel} was enabled')
            elif bool(status[1]) is True:
                self.logger.info(f'Power Channel {mp_channel} is locked by sys')
                self.logger.info(f'Power is disabled and can not be enabled for the channel {mp_channel}')
                return None
            elif bool(status[2]) is True:
                self.logger.info(f'Power Channel {mp_channel} is locked by user')
                self.logger.info(f'Power is disabled and can not be enabled on channel {mp_channel} through this routine')
                return None
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'Error while enabling Power of channel {mp_channel}')

        dev = AnalysisUtils().open_yaml_file(file=file, directory=directory)
        self.logger.info('Reading from yaml to get dictionary items')
        # yaml file is needed to get the object dictionary items
        _adc_channels_reg = dev["adc_channels_reg"]["adc_channels"]
        _adc_index = list(dev["adc_channels_reg"]["adc_index"])[0]
        _channelItems = [int(channel) for channel in list(_adc_channels_reg)]
        _channelDesc: List[Any] = [dev["adc_channels_reg"]["adc_channels"][str(_channelItems[i])] for i in
                                   range(len(_channelItems))]

        dev2 = AnalysisUtils().open_yaml_file(file=file, directory=directory)
        _mon_index = list(dev2["adc_channels_reg"]["mon_index"])[0]
        items = list(dev2["Application"]["index_items"]["0x2310"]["subindex_items"])
        _mon_channelItems = [int(channel) for channel in list(items)]
        _mon_channelDesc: List[Any] = [dev2["Application"]["index_items"]["0x2310"]["subindex_items"]
                                       [str(_mon_channelItems[i])] for i in range(len(_mon_channelItems))]
        for i in range(len(_mon_channelDesc)):
            string = BeautifulSoup(_mon_channelDesc[i], features="lxml")
            _mon_channelDesc[i] = string.get_text()

        self.logger.info(f'Reading ADC channels of Mops with ID {node_id}')
        mops_readout = [[None for _ in range(3)] for _ in range(len(_channelItems))]  # indexing: [y][x]
        mops_monitoring = [[None for _ in range(3)] for _ in range(len(_mon_channelItems))]

        if can_channel == can_config.can_0_settings['Channel']:
            timeout = can_config.can_0_settings['Timeout']
        else:
            timeout = can_config.can_1_settings['Timeout']

        # Read ADC channels
        for i in range(0, len(_channelItems)):
            subindex = _channelItems[i] - 2
            data_point = await self.read_sdo_can(node_id, int(_adc_index, 16), subindex, can_channel, timeout)
            # data_point = randint(0, 100)
            await asyncio.sleep(0.01)
            if data_point is not None:
                adc_converted = Analysis().adc_conversion(str(_channelDesc[i]), data_point)
                adc_converted = round(adc_converted, 3)
                # adc_converted = adc_converted * 100 * randint(10, 100)
                mops_readout[i][0] = (_channelItems[i])  # adc channel_index
                # mops_readout[i][1] = data_point
                mops_readout[i][1] = adc_converted  # datapoint of channel read
                mops_readout[i][2] = _channelDesc[i]  # description of channel
                self.logger.info(f'Got data for ADC channel {subindex} = {data_point}')
            else:
                # has to be defined
                pass

        for i in range(len(_mon_channelItems)):
            subindex = _mon_channelItems[i]
            data_point = await self.read_sdo_can(node_id, int(_mon_index, 16), subindex, can_channel, timeout)
            # data_point = randint(0, 100)
            await asyncio.sleep(0.01)
            if data_point is not None:
                adc_converted = Analysis().adc_conversion(str(_channelDesc[i]), data_point)
                adc_converted = round(adc_converted, 3)
                # adc_converted = adc_converted * 100 * randint(10, 100)
                mops_monitoring[i][0] = (_mon_channelItems[i])  # adc channel_index
                # mops_monitoring[i][1] = data_point
                mops_monitoring[i][1] = adc_converted  # datapoint of channel read
                mops_monitoring[i][2] = _mon_channelDesc[i]  # description of channel
                self.logger.info(f'Got data for ADC channel {subindex} = {data_point}')
            else:
                # has to be defined
                pass

        self.receive_queue = queue.Queue()
        return mops_readout, mops_monitoring

    async def confirm_nodes(self, channel=None, node_id=None, timeout=1000, max_data_bytes=8):
        self.logger.info('Testing Connection')

        if node_id is None or channel is None:
            self.logger.error('Missing parameter. Can not confirm nodes')
            return 0
        ####################################################################
        # for testing
        # device_info = await self.read_device_info(node_id, channel)
        # return True, device_info
        ####################################################################
        cobid_tx = 0x700 + node_id
        can_config.sem_config_block.acquire()
        self.logger.info("Start Communication")
        try:
            await self.write_can_message(channel, cobid_tx, [0, 0, 0, 0, 0, 0, 0, 0], timeout=timeout)
            self.current_channel = channel
            self.current_subindex = 0
            self.cobid_ret = cobid_tx
        except Exception as e:
            self.logger.exception(e)
            self.cnt['SDO read request timeout'] += 1
            self.logger.error("Confirming node was not possible")
            return False

        can_config.sem_recv_block.release()
        self.logger.info("Send Thread is waiting for receive thread to finish socket read")
        can_config.sem_read_block.acquire()
        self.logger.info("Receiving is finished. Processing received data")
        can_config.sem_config_block.release()
        self.logger.info("Communication finished")

        while not self.receive_queue.empty():
            frame = self.receive_queue.get()
            if frame is not None:
                cobid_rx, ret, dlc, flag, t, error_frame = (frame.arbitration_id, frame.data,
                                                            frame.dlc, frame.is_extended_id,
                                                            frame.timestamp, frame.is_error_frame)
                if cobid_rx == cobid_tx and (ret[0] == 0x85 or ret[0] == 0x05 and dlc == max_data_bytes):
                    self.logger.info(f'Connection to Mops verified. NodeID: {node_id}')
                    self.receive_queue = queue.Queue()
                    device_info = await self.read_device_info(node_id, channel)
                    return True, device_info
        else:
            self.logger.error(f'Connection Error! Mops NodeID: {node_id}')
            self.receive_queue = queue.Queue()
            return False, None

    async def read_device_info(self, node_id, channel, timeout=1000, max_data_bytes=8):
        dev2 = AnalysisUtils().open_yaml_file(file="mops_config.yml", directory="config_files")
        device_info = []
        #####################################################################
        # for testing
        # for index in list(dev2["adc_channels_reg"]["conf_index"]):
        #     readout = []
        #     for subindex in dev2["Application"]["index_items"][index]["subindex_items"]:
        #         desc = BeautifulSoup(dev2["Application"]["index_items"][index]["subindex_items"][subindex],
        #                              features="lxml")
        #         readout.append(randint(0, 10))
        #         readout.append(desc.get_text())
        #     device_info.append(readout)
        # return device_info
        ####################################################################
        for index in list(dev2["adc_channels_reg"]["conf_index"]):
            for subindex in dev2["Application"]["index_items"][index]["subindex_items"]:
                readout = []
                cobid_tx = 0x600 + node_id
                cobid_ret = 0x580 + node_id
                msg = [0 for _ in range(max_data_bytes)]
                msg[0] = 0x40
                msg[1], msg[2] = int(index, 16).to_bytes(2, 'little')
                msg[3] = int(subindex)

                can_config.sem_config_block.acquire()
                self.logger.info("Start Communication")
                try:
                    self.logger.info(f"Sending with this information: index:{index}, subindex{subindex}")
                    await self.write_can_message(channel, cobid_tx, msg, timeout=timeout)
                    self.current_subindex = int(subindex)
                    self.current_channel = channel
                    self.cobid_ret = cobid_ret
                except can.CanError as e:
                    self.logger.exception(e)
                    self.cnt['SDO read request timeout'] += 1
                    return None

                can_config.sem_recv_block.release()
                self.logger.info("Send Thread is waiting for receive thread to finish socket read")
                # Wait for can-message
                can_config.sem_read_block.acquire()
                self.logger.info("Receiving is finished. Processing received data")
                can_config.sem_config_block.release()
                self.logger.info("Communication finished")

                while not self.receive_queue.empty():
                    frame = self.receive_queue.get()
                    if frame is not None:
                        cobid_rx, ret, dlc, flag, t, error_frame = (frame.arbitration_id, frame.data,
                                                                    frame.dlc, frame.is_extended_id,
                                                                    frame.timestamp, frame.is_error_frame)
                        if cobid_rx == cobid_ret and dlc == max_data_bytes:
                            desc = BeautifulSoup(dev2["Application"]["index_items"][index]["subindex_items"][subindex],
                                                 features="lxml")
                            self.receive_queue = queue.Queue()
                            n_data_bytes = 4 - ((ret[0] >> 2) & 0b11) if ret[0] != 0x42 else 4
                            data = []
                            for i in range(n_data_bytes):
                                data.append(ret[4 + i])
                            self.logger.info('Got data %s', data)
                            readout.append(int.from_bytes(data, 'little'))
                            readout.append(desc.get_text())
                    device_info.append(readout)
        return device_info

    async def write_can_message(self, channel: int, cobid: int, data, timeout: int):
        # Writing function for SocketCAN interface
        msg = can.Message(arbitration_id=cobid, data=data, is_extended_id=False, is_error_frame=False)
        try:
            # self.logger.info(f"Sending CAN msg on Channel {channel}: {msg}")
            can_config.send(channel, msg, timeout)
        except can.CanError as e:
            self.logger.error(f'ERROR while sending msg on channel {channel}')
            self.logger.error(f"{e}")
