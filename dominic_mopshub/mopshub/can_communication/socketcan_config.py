# This File is setting up the CAN Channels on the RPI on the beginning
# Possible updates: Watchdog on Channel Health while system is running

import logging
import can
import subprocess
import threading

from additional_scripts import logger_setup
from additional_scripts.analysis_utils import AnalysisUtils
from can_communication.watchdog_can_interface import WATCHCan


class CanConfig(WATCHCan):
    """description of class"""

    def __init__(self, file='can_config.yml', directory='config_files'):

        WATCHCan.__init__(self)
        self._file = file
        self._directory = directory
        self.logger = logging.getLogger('mopshub_log.can_config')

        self._can_channels = ['channel0', 'channel1']
        self._can_settings_attr = ['Bitrate', 'Channel', 'SamplePoint', 'SJW', 'tseg1', 'tseg2', 'ipAddress', 'Timeout']

        self.can_0_settings = {}
        self.can_1_settings = {}

        _canSettings = AnalysisUtils().open_yaml_file(file=self._file, directory=self._directory)

        self._interface = _canSettings['CAN_Interfaces']
        self.sem_read_block = threading.Semaphore(value=0)
        self.sem_recv_block = threading.Semaphore(value=0)
        self.sem_config_block = threading.Semaphore()
        self.ch0 = None
        self.ch1 = None
        self._busOn0 = False
        self._busOn1 = False
        can.util.set_logging_level('warning')

        for channel in self._can_channels:
            for value in _canSettings[channel]:
                if channel == self._can_channels[0]:
                    self.can_0_settings[f'{value}'] = _canSettings[channel][f'{value}']
                else:
                    self.can_1_settings[f'{value}'] = _canSettings[channel][f'{value}']

    def send(self, channel: int, msg: can.message, timeout: int):
        try:
            if channel == self.can_0_settings['Channel']:
                if self._busOn0 is True:
                    self.ch0.send(msg, timeout)
                else:
                    self.restart_channel_connection(channel)
                    self.ch0.send(msg, timeout)
            elif channel == self.can_1_settings['Channel']:
                if self._busOn1 is True:
                    self.ch1.send(msg, timeout)
                else:
                    self.restart_channel_connection(channel)
                    self.ch1.send(msg, timeout)
        except can.CanError:
            return can.CanError

    def receive(self, channel: int):
        try:
            if channel == self.can_0_settings['Channel']:
                if self._busOn0 is True:
                    frame = self.ch0.recv(0.0)
                    return frame
                else:
                    self.restart_channel_connection(channel)
                    frame = self.ch0.recv(0.0)
                    return frame
            elif channel == self.can_1_settings['Channel']:
                if self._busOn1 is True:
                    frame = self.ch1.recv(0.0)
                    return frame
                else:
                    self.restart_channel_connection(channel)
                    frame = self.ch0.recv(0.0)
                    return frame
        except can.CanError:
            return can.CanError

    def can_setup(self, channel: int):
        self.logger.info("Resetting CAN Interface as soon as communication threads are finished")
        self.sem_config_block.acquire()
        self.logger.info("Resetting CAN Interface")
        if channel == self.can_0_settings['Channel']:
            if self._busOn0:
                self.ch0.shutdown()
            subprocess.call(['sh', './can_setup.sh', "can0", f"{self.can_0_settings['Bitrate']}",
                             f"{self.can_0_settings['tseg1']}", f"{self.can_0_settings['tseg2']}",
                             f"{self.can_0_settings['SJW']}", f"{self.can_0_settings['SamplePoint']}"],
                            cwd='/home/pi/mopsopc-for-beginners-master/config_files')
            self.set_channel_connection(self.can_0_settings['Channel'])
        elif channel == self.can_1_settings['Channel']:
            if self._busOn1:
                self.ch1.shutdown()
            subprocess.call(['sh', './can_setup.sh', "can1", f"{self.can_1_settings['Bitrate']}",
                             f"{self.can_1_settings['tseg1']}", f"{self.can_1_settings['tseg2']}",
                             f"{self.can_1_settings['SJW']}", f"{self.can_1_settings['SamplePoint']}"],
                            cwd='/home/pi/mopsopc-for-beginners-master/config_files')
            self.set_channel_connection(self.can_1_settings['Channel'])

        self.logger.info(f"Channel {channel} was set")
        self.sem_config_block.release()
        self.logger.info("Resetting of CAN Interface finished. Returning to communication.")

    def set_channel_connection(self, channel: int):
        """Bind |CAN| socket
           Set the internal attribute for the |CAN| channel
           The function is important to initialise the channel
            """
        try:
            if channel == self.can_0_settings['Channel']:
                channel = "can" + str(self.can_0_settings['Channel'])
                self.ch0 = can.interface.Bus(bustype=self._interface, channel=channel,
                                             bitrate=self.can_0_settings['Bitrate'])
                self.ch0.RECV_LOGGING_LEVEL = 0
                self._busOn0 = True
                self.logger.info(f'Setting of channel {channel} worked.')
            elif channel == self.can_1_settings['Channel']:
                channel = "can" + str(self.can_1_settings['Channel'])
                self.ch1 = can.interface.Bus(bustype=self._interface, channel=channel,
                                             bitrate=self.can_1_settings['Bitrate'])
                self.ch1.RECV_LOGGING_LEVEL = 0
                self._busOn1 = True
                self.logger.info(f'Setting of channel {channel} worked.')
            else:
                self.logger.error(f"Setting of Channel {channel} did not worked because of missing reference in dict")
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'Error by setting channel {channel}.')

    def stop_channel(self, channel: int):
        """Close |CAN| channel
            Make sure that this is called so that the connection is closed in a
            correct manner. When this class is used within a :obj:`with` statement
            this method is called automatically when the statement is exited.
            """
        self.logger.info(f'Going to stop channel {channel}')
        if channel == self.can_0_settings['Channel']:
            if self._busOn0:
                self.ch0.shutdown()
                self._busOn0 = False
                self.logger.info(f'Channel {channel} was stopped successful.')
        elif channel == self.can_1_settings['Channel']:
            if self._busOn1:
                self.ch1.shutdown()
                self._busOn1 = False
                self.logger.info(f'Channel {channel} was stopped successful.')
        else:
            self.logger.error(f"Stopping Channel {channel} did not worked because of missing reference in dict")

    def restart_channel_connection(self, channel: int):
        """Restart |CAN| channel.
        for threaded application, busOff() must be called once for each handle.
        The same applies to busOn() - the physical channel will not go off bus
        until the last handle to the channel goes off bus.
        """
        self.logger.info(f'Restarting Channel {channel}.')
        if channel == self.can_0_settings['Channel']:
            if self._busOn0:
                self.ch0.shutdown()
                self.logger.info(f'Channel {channel} was stopped.')
                self._busOn0 = False
                self.set_channel_connection(channel)
                self.logger.info(f'Reset of Channel {channel} finished.')
        elif channel == self.can_1_settings['Channel']:
            if self._busOn1:
                self.ch1.shutdown()
                self.logger.info(f'Channel {channel} was stopped.')
                self._busOn1 = False
                self.set_channel_connection(channel)
                self.logger.info(f'Reset of Channel {channel} finished.')
        else:
            self.logger.error(f"Restart of Channel {channel} did not worked because of missing reference in dict")


can_config = CanConfig()
can_config.watchdog_notifier.subscribe("restart Interface", can_config.can_setup)
