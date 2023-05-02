import asyncio
import logging
import argh
from itertools import product
import time
from datetime import datetime

from additional_scripts import logger_setup
from opcua_server.opc_server import MOPSHUBCrate
from cic_control.cic_adc_readout import CICreadout
from can_communication.can_wrapper import CANWrapper
from cic_control.power_config import power_signal
from can_communication.socketcan_config import can_config


class MHfB(MOPSHUBCrate, CICreadout, CANWrapper):
    """description of class"""

    def __init__(self):

        self.config_files_directory = 'config_files'
        self.server_config_file = 'server_config.yaml'
        self.can_config_file = 'can_config.yml'
        self.mops_config_file = 'mops_config.yml'

        self.mopshub_crate = MOPSHUBCrate()
        self.wrapper = CANWrapper()
        self.cic_card = CICreadout()
        self.maxRatings = [100, 100, 100, 100, 100]
        self.minRatings = [-1, -1, -1, -1, -1]
        self.confirmed_nodes = [[None for _ in range(2)] for _ in range(len(self.mopshub_crate.Bus))]
        self.avg_time = 0

        self.logger = logging.getLogger('mopshub_log.opc')

    async def main(self):

        self.mopshub_crate.notifier.subscribe("new_can_config", reconfigure_can)

        data = self.mopshub_crate.load_configuration(self.config_files_directory, self.server_config_file)

        self.logger.info('Starting Server')
        await self.mopshub_crate.init(self.server_config_file, self.can_config_file, self.config_files_directory)
        await self.mopshub_crate.browse_server()

        for cic_id, bus_id, mops_id in product(range(4), range(1, 33), range(2)):
            if (self.mopshub_crate.CICs[cic_id] is not None) and (f"Bus {bus_id}" in data[f"CIC {cic_id}"]):
                if power_signal.locked_by_sys[bus_id - 25] is True:
                    await self.mopshub_crate.write_pe_status(cic_id, bus_id, "OFF")
                elif power_signal.locked_by_sys[bus_id - 25] is False:
                    await self.mopshub_crate.write_pe_status(cic_id, bus_id, "ON")

        await self.check_nodes()

        async with self.mopshub_crate:
            counter = 0
            total_time = 0
            while True:
                for cic_id, bus_id, mops_id in product(range(4), range(1, 33), range(2)):
                    if (self.mopshub_crate.CICs[cic_id] is not None) and (
                            f"Bus {bus_id}" in data[f"CIC {cic_id}"]) and (
                            f"MOPS {mops_id}" in data[f"CIC {cic_id}"][f"Bus {bus_id}"]) and (
                            power_signal.locked_by_sys[bus_id - 25] is False) and (
                            power_signal.locked_by_user[bus_id - 25] is False) and (
                            self.confirmed_nodes[bus_id - 1][mops_id] is True):
                        counter += 1
                        can_channel = 1  # it is important to specify when we want to use which can channel as
                        # there is no difference between can0 and can1 at the end

                        # exact specification for: mops_index, channel_index, adc_value, cic_adc_channel, cic_adc_value
                        start = time.time()
                        readout_mops, monitoring_mops = await self.wrapper.read_adc_channels(self.mops_config_file,
                                                                                             self.config_files_directory,
                                                                                             mops_id, bus_id,
                                                                                             can_channel)
                        # readout_adc = self.cic_card.dummy_read()
                        readout_adc = self.cic_card.read_adc(0, bus_id, 1)
                        end = time.time()
                        total_time += (end-start)
                        self.avg_time = total_time/counter

                        if monitoring_mops is not None:
                            self.logger.info('Writing MOPS monitoring data to their nodes')
                            for i in range(len(monitoring_mops)):
                                if None not in monitoring_mops[i]:
                                    value = monitoring_mops[i][1]
                                    desc = monitoring_mops[i][2]
                                    await self.mopshub_crate.write_mops_mon(cic_id, bus_id, mops_id, desc, value)

                        if readout_mops is not None:
                            self.logger.info('Writing MOPS Readout to their nodes')
                            for i in range(len(readout_mops)):
                                if None not in readout_mops[i]:
                                    adc_index = readout_mops[i][0]
                                    value = readout_mops[i][1]
                                    # exact specification for: mops_index, channel_index, cic_adc_channel
                                    await self.mopshub_crate.write_mops_adc(cic_id, bus_id, mops_id, adc_index,
                                                                            value)

                        if readout_adc is not None:
                            self.logger.info('Writing CIC Readout to their nodes')
                            for adc_channel in range(len(readout_adc)):
                                if adc_channel is not None:
                                    value = readout_adc[adc_channel]
                                    # exact specification for: mops_index, channel_index, cic_adc_channel
                                    await self.mopshub_crate.write_cic_adc(cic_id, bus_id, adc_channel, value)

                        self.logger.info(f"Readout MOPS {mops_id} finished")
                        print(self.wrapper.good_frames)
                        print(self.wrapper.err_counter)
                        print(self.avg_time)
                self.logger.info('Readout finished')
                await asyncio.sleep(0.5)

    async def check_nodes(self):
        self.logger.info("Checking Nodes")
        data = self.mopshub_crate.load_configuration(self.config_files_directory, self.server_config_file)
        confirmed_nodes = [[None for _ in range(2)] for _ in range(len(self.mopshub_crate.Bus))]

        for cic_id, bus_id, mops_id in product(range(4), range(1, 33), range(2)):
            if (self.mopshub_crate.CICs[cic_id] is not None) and (
                    f"Bus {bus_id}" in data[f"CIC {cic_id}"]) and (
                    f"MOPS {mops_id}" in data[f"CIC {cic_id}"][f"Bus {bus_id}"]) and (
                    power_signal.locked_by_sys[bus_id - 25] is False):
                self.logger.info(f"Checking Node on CIC {cic_id}, Bus {bus_id} with NodeID {mops_id}")
                self.wrapper.mp_switch(bus_id, 1)
                confirmed_nodes[bus_id - 1][mops_id], device_info = await self.wrapper.confirm_nodes(1, mops_id)
                for i in range(len(device_info)):
                    await self.mopshub_crate.write_mops_conf(cic_id, bus_id, mops_id, device_info[i][1],
                                                             device_info[i][0])

        self.confirmed_nodes = confirmed_nodes

    def start_system(self):
        """
        Start the System by first checking all CIC cards and check their Power status.
        After that we going to confirm all Mops Nodes by their given ID
        """

        power_signal.set_power_off()
        for i in range(len(power_signal.current_status_table)):
            error_cnt = 0
            power_signal.power_on(i)
            time.sleep(0.1)
            readout_adc = self.cic_card.read_adc(0, i, 1)
            time.sleep(0.1)
            for j in range(1, len(readout_adc)):
                if error_cnt == 0:
                    if readout_adc[j] >= self.maxRatings[j] or readout_adc[j] < 0:
                        self.logger.error(f"On Bus {i + 25} the ADC Value of Channel {j} is out of "
                                          f"the recommended specification")
                        self.logger.warning(f"Going to turn power off on bus {i + 25}")
                        power_signal.power_off(i)
                        power_signal.locked_by_sys[i] = True
                        error_cnt += 1
                    elif readout_adc[j] == 0 and j in range(0, len(readout_adc) - 1):
                        self.logger.warning(f"Could not connect to ADC on Bus {i + 25}")
                        power_signal.power_off(i)
                        power_signal.locked_by_sys[i] = True
                        error_cnt += 1

            if error_cnt == 0:
                self.logger.info(f"Bus {i} was approved and can be used")
                power_signal.locked_by_sys[i] = False
            else:
                self.logger.info(f"Bus {i} failed approving process and is locked")
                power_signal.locked_by_sys[i] = True

        self.logger.info(power_signal.current_status_table)
        self.logger.info(f"Locked by sys: {power_signal.locked_by_sys}")
        self.logger.info(f"Locked by user: {power_signal.locked_by_user}")


def start():
    """Start an OPC UA server for a given crate configuration file"""
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(opc.main())
        loop.run_forever()
    except KeyboardInterrupt:
        can_config.stop()
        can_config.stop_channel(0)
        can_config.stop_channel(1)
        opc.wrapper.stop()


def reconfigure_can():
    can_config.can_setup()
    opc.check_nodes()
    opc.logger.info('CAN settings were reconfigured')


if __name__ == '__main__':
    opc = MHfB()
    opc.start_system()
    parser = argh.ArghParser()
    parser.add_commands([start])
    parser.dispatch()
    start()
