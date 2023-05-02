import logging
import sys
import os

from EventNotifier import Notifier
from logging import Logger
from yaml import load, dump
from itertools import product

from additional_scripts import logger_setup
from cic_control.power_config import power_signal
from additional_scripts.analysis_utils import AnalysisUtils
from can_communication.socketcan_config import can_config

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
sys.path.insert(0, "../..")


class POPULATEAddressSpace:

    def __init__(self, server):

        self.Server = server
        self.idx = 0
        self.mopshub_crate_object = None
        self.CICs = [None for _ in range(4)]
        self.Bus = [None for _ in range(32)]
        self.Mops = [[None for _ in range(2)] for _ in range(len(self.Bus))]
        self.can_attr = ['Channel', 'Bitrate', 'SamplePoint', 'SJW', 'tseg1', 'tseg2', 'Timeout']
        self.can_config = [[None for _ in range(len(self.can_attr))] for _ in range(2)]

        self.notifier = Notifier(["new_can_config"])

        self.logger = logging.getLogger('mopshub_log.crate')
        self._logger: Logger = logging.getLogger('asyncua')
        self._logger.setLevel(logging.DEBUG)

        self.defaults = {
            "ADC Channel Default Converter": 'Raw',
            "MOPS Default Location": 'Unknown',
            "MOPS Default Status": 0,
            "MOPS Default Port": 0,
            "MOPS Configuration Default Trimming": 0
        }

    async def disable_power(self, parent):
        logging.warning('Power OFF')
        node = self.Server.get_node(f"{parent}")
        children = await node.get_children()

        status_node = None
        channel = None
        try:
            for child in children:
                desc = await child.read_description()
                if desc.Text == 'Bus ID':
                    channel = await child.get_value()
                if desc.Text == 'Current Status':
                    status_node = child
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("An Error occurred by switching OFF Channel")

        status = power_signal.check_status(channel)
        if bool(status[1]) is False and status_node is not None and channel is not None:
            power_signal.power_off(channel, True)
            status = power_signal.check_status(channel)
            self.logger.info("Power of Channel %s was switched to OFF by User(Data,Locked: %s, %s)",
                             channel, str(status[0]), str(status[2]))
            await status_node.write_value("OFF")
            return []
        elif bool(status[1]) is True:
            self.logger.error("Power of the Channel was locked from sys while start up", channel)
            return []

    async def enable_power(self, parent):
        logging.warning('Power ON')
        node = self.Server.get_node(f"{parent}")
        children = await node.get_children()

        status_node = None
        channel = None
        try:
            for child in children:
                desc = await child.read_description()
                if desc.Text == 'Bus ID':
                    channel = await child.get_value()
                if desc.Text == 'Current Status':
                    status_node = child
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("An Error occurred by switching ON Channel")

        status = power_signal.check_status(channel)
        if bool(status[1]) is False and status_node is not None and channel is not None:
            power_signal.power_on(channel, False)
            status = power_signal.check_status(channel)
            self.logger.info("Power of Channel %s was switched to ON by User(Data,Locked: %s, %s)",
                             channel, str(status[0]), str(status[2]))
            await status_node.write_value("ON")
            return []
        elif bool(status[1]) is True:
            self.logger.error("Power of the Channel was locked from sys while start up", channel)
            return []

    async def configure_can(self, parent):
        node = self.Server.get_node(f"{parent}")
        children = await node.get_children()

        channel = None
        try:
            for child in children:
                desc = await child.read_description()
                if desc.Text == 'Channel':
                    channel = await child.get_value()
        except Exception as e:
            self.logger.exception(e)

        new_config = [None for _ in range(len(self.can_attr))]
        for attr in range(len(self.can_attr)):
            if channel is not None:
                new_config[attr] = await self.can_config[channel][attr].get_value()

        config_dict = {}

        for i in range(len(self.can_attr)):
            config_dict[self.can_attr[i]] = new_config[i]

        if config_dict['Channel'] == can_config.can_0_settings['Channel']:
            can_config.can_0_settings.update(config_dict)
            self.logger.info(can_config.can_0_settings)
            self.notifier.raise_event("new_can_config")
        elif config_dict['Channel'] == can_config.can_1_settings['Channel']:
            can_config.can_1_settings.update(config_dict)
            self.logger.info(can_config.can_1_settings)
            self.notifier.raise_event("new_can_config")

    def load_configuration(self, directory: str, config_file: str):
        """Load configuration YAML and insert the system defaults where the user didn't specify them.
        Give warning where user didn't specify a default.

        :type directory: str
        :param directory: Folder of the config_file
        :type config_file: str
        :param config_file: Configuration YAML containing active MOPS and custom init values, converter, aliases, etc.
        :return: Dict populated with necessary default values
        """
        # Get configuration data
        filename = os.path.join(directory, config_file)
        with open(filename, 'r') as fstream:
            data = load(fstream, Loader=Loader)
            fstream.close()
            if logging.DEBUG >= logging.root.level:
                dump(data, Dumper=Dumper)
                self._logger.info(f"Configured with {config_file}")
            if "Crate ID" not in data:
                self._logger.error(f"No crate ID specified in {config_file}")
                raise KeyError(f"No crate ID specified in {config_file}")
            # Check defaults
            for k in self.defaults:
                if k not in data:
                    self._logger.warning(f"No {k} specified in {config_file}, using {self.defaults[k]}")
                    data[k] = self.defaults[k]
        return data

    async def populate(self, server_config_file: str, can_config_file: str, directory: str):

        self.mopshub_crate_object = await self.Server.nodes.objects.add_object(self.idx, "MOPSHUB Crate")

        data = self.load_configuration(directory, server_config_file)
        can_settings = AnalysisUtils().open_yaml_file(file=can_config_file, directory=directory)

        # Create crate ID variable
        await self.mopshub_crate_object.add_variable(self.idx, "Crate ID", data["Crate ID"])

        # Create Objects for configure CAN settings
        for i in range(0, 2):
            can_obj = await self.mopshub_crate_object.add_object(self.idx, f"Config CAN{i}")
            for attr in range(len(self.can_attr)):
                self.can_config[i][attr] = await can_obj.add_variable(self.idx, self.can_attr[attr],
                                                                      int(can_settings[f'channel{i}'][
                                                                              self.can_attr[attr]]))
                if self.can_attr[attr] == 'Channel':
                    await self.can_config[i][attr].set_writable(False)
                else:
                    await self.can_config[i][attr].set_writable(True)
            await can_obj.add_method(self.idx, f"Configure CAN{i}", self.configure_can)

        # Create CIC card objects
        for cic_id in range(len(self.CICs)):
            if f"CIC {cic_id}" in data:
                self.CICs[cic_id] = await self.mopshub_crate_object.add_object(self.idx, f"CIC {cic_id}")

        # Create Can Bus objects
        for cic_id, bus_id in product(range(len(self.CICs)), range(1, len(self.Bus) + 1)):
            if (self.CICs[cic_id] is not None) and (f"Bus {bus_id}" in data[f"CIC {cic_id}"]):
                self.Bus[bus_id - 1] = await self.CICs[cic_id].add_object(self.idx, f"CANBus {bus_id}")

                await self.Bus[bus_id - 1].add_variable(self.idx, "Bus ID", bus_id)

                # Create Power Enable Child for every Bus
                pe_object = await self.Bus[bus_id - 1].add_object(self.idx, f"PE Signal CANBus {bus_id}")
                await pe_object.add_variable(self.idx, "Bus ID", bus_id)
                await pe_object.add_variable(self.idx, "Description", f"Control of th Power of Bus {bus_id}")
                pe_status = await pe_object.add_variable(self.idx, "Current Status", "OFF")
                await pe_status.set_writable(True)

                await pe_object.add_method(self.idx, f"Power Disable Bus {bus_id}",
                                           self.disable_power)

                await pe_object.add_method(self.idx, f"Power Enable Bus {bus_id}",
                                           self.enable_power)

                # Create CIC ADC Child for every Bus
                cic_adc_object = await self.Bus[bus_id - 1].add_object(self.idx, f"ADC CANBus {bus_id}")

                for channel_id in range(5):
                    channel_object = await cic_adc_object.add_object(self.idx, f"ADCChannel {channel_id:02}")

                    if channel_id == 0:
                        await channel_object.add_variable(self.idx, "Description", "UH for Current Monitoring")
                    elif channel_id == 1:
                        await channel_object.add_variable(self.idx, "Description", "UL for Current Monitoring")
                    elif channel_id == 2:
                        await channel_object.add_variable(self.idx, "Description", "Voltage Monitoring")
                    elif channel_id == 3:
                        await channel_object.add_variable(self.idx, "Description", "Temperature Monitoring")
                    elif channel_id == 4:
                        await channel_object.add_variable(self.idx, "Description", "GND Monitoring")

                    await channel_object.add_variable(self.idx, "Physical Unit", "Voltage")
                    await channel_object.add_variable(self.idx, "monitoringValue", 0.0)

        # Create MOPS objects
        for cic_id, bus_id, mops_id in product(range(len(self.CICs)), range(1, len(self.Bus) + 1), range(2)):
            if (self.CICs[cic_id] is not None) and (f"Bus {bus_id}" in data[f"CIC {cic_id}"]) and (
                    f"MOPS {mops_id}" in data[f"CIC {cic_id}"][f"Bus {bus_id}"]):

                bus_data = data[f"CIC {cic_id}"][f"Bus {bus_id}"]
                self.Mops[bus_id - 1][mops_id] = await self.Bus[bus_id - 1].add_object(self.idx, f"MOPS {mops_id}")
                mops_data = bus_data[f"MOPS {mops_id}"]

                # Specify location
                if "Location" in mops_data:
                    await self.Mops[bus_id - 1][mops_id].add_variable(self.idx, "location", mops_data["Location"])
                else:
                    await self.Mops[bus_id - 1][mops_id].add_variable(self.idx, "location",
                                                                      data["MOPS Default Location"])

                # Status and portNumber variables
                if "Status" in mops_data:
                    status_var = await self.Mops[bus_id - 1][mops_id].add_variable(self.idx, "status",
                                                                                   mops_data["Status"])
                    await status_var.set_writable()
                else:
                    status_var = await self.Mops[bus_id - 1][mops_id].add_variable(self.idx, "status",
                                                                                   data["MOPS Default Status"])
                    await status_var.set_writable()
                if "Port" in mops_data:
                    port_var = await self.Mops[bus_id - 1][mops_id].add_variable(self.idx, "portNumber",
                                                                                 mops_data["Port"])
                    await port_var.set_writable()
                else:
                    port_var = await self.Mops[bus_id - 1][mops_id].add_variable(self.idx, "portNumber",
                                                                                 data["MOPS Default Port"])
                    await port_var.set_writable()

                await self.Mops[bus_id - 1][mops_id].add_variable(self.idx, "NodeID", mops_id)

                information_object = await self.Mops[bus_id - 1][mops_id].add_object(self.idx, "MOPSInfo")
                await information_object.add_variable(self.idx, "Device type", "")
                await information_object.add_variable(self.idx, "Error register", "")
                await information_object.add_variable(self.idx, "COB-ID SYNC", "")
                await information_object.add_variable(self.idx, "COB-ID EMCY", "")
                await information_object.add_variable(self.idx, "Number of entries", "")
                await information_object.add_variable(self.idx, "Vendor Id", "")
                await information_object.add_variable(self.idx, "ADC trimming bits", "")

                # Add MOPSMonitoring Object
                monitoring_object = await self.Mops[bus_id - 1][mops_id].add_object(self.idx, "MOPSMonitoring")
                await monitoring_object.add_variable(self.idx, "Number of entries", 0.0)
                await monitoring_object.add_variable(self.idx, "VBANDGAP", 0.0)
                await monitoring_object.add_variable(self.idx, "VGNDSEN", 0.0)
                await monitoring_object.add_variable(self.idx, "VCANSEN", 0.0)

                # Add MOPSConfiguration Object
                configuration_object = await self.Mops[bus_id - 1][mops_id].add_object(self.idx, "MOPSConfiguration")
                await configuration_object.add_variable(self.idx, "readFEMonitoringValues", 0.0)
                if "Trimming" in mops_data:
                    trimming_var = await configuration_object.add_variable(self.idx, "ADCTrimmingBits",
                                                                           mops_data["Trimming"])
                    await trimming_var.set_writable()
                else:
                    trimming_var = await configuration_object.add_variable(self.idx, "ADCTrimmingBits",
                                                                           data["MOPS Configuration Default Trimming"])
                    await trimming_var.set_writable()

                # Add ADC Channels
                for channel_id in range(3, 35):
                    channel_object = await self.Mops[bus_id - 1][mops_id].add_object(self.idx,
                                                                                     f"ADCChannel {channel_id:02}")
                    await channel_object.add_variable(self.idx, f"ADC Channel ID", channel_id)

                    if f"ADC Channel {channel_id}" in mops_data:
                        channel_data = mops_data[f"ADC Channel {channel_id}"]
                        if "Converter" not in channel_data:
                            channel_data["Converter"] = data["ADC Channel Default Converter"]
                        if "Alias" not in channel_data:
                            channel_data["Alias"] = channel_data["Converter"]

                        await channel_object.add_variable(self.idx, "Converter", channel_data["Converter"])
                        await channel_object.add_variable(self.idx, "physicalParameter", channel_data["Alias"])
                        if channel_data["Converter"] == 'Raw':
                            await channel_object.add_variable(self.idx, "monitoringValue", 0.0)
                        else:
                            await channel_object.add_variable(self.idx, "monitoringValue", 0.0)
                    else:
                        await channel_object.add_variable(self.idx, "Converter", data["ADC Channel Default Converter"])
                        await channel_object.add_variable(self.idx, "physicalParameter",
                                                          data["ADC Channel Default Converter"])
                        if data["ADC Channel Default Converter"] == 'Raw':
                            await channel_object.add_variable(self.idx, "monitoringValue", 0.0)
                        else:
                            await channel_object.add_variable(self.idx, "monitoringValue", 0.0)
