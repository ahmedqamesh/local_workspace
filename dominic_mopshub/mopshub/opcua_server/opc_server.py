import asyncua
import logging
import sys

from logging import Logger
from asyncua import Node
from EventNotifier import Notifier

from additional_scripts import logger_setup
from opcua_server.populate_address_space import POPULATEAddressSpace
from opcua_server.find_node_id import FINDNodeID
from opcua_server.browse_server_structure import BROWSEServer

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
sys.path.insert(0, "../..")


class MOPSHUBCrate(POPULATEAddressSpace, FINDNodeID, BROWSEServer):
    def __init__(self, endpoint: str = 'opc.tcp://0.0.0.0:4840/freeopcua/server/',
                 namespace: str = 'http://examples.freeopcua.github.io', *args, **kwargs):
        """Constructor for MOPSHUBCrate
        :type namespace: str
        :type endpoint: str
        :param endpoint: The server endpoint (hint: 127.0.0.1 hosts on YOUR machine,
                         0.0.0.0 exposes the server to the network as well)
        :param namespace: The namespace
        """

        self.Server = asyncua.Server()
        BROWSEServer.__init__(self, self.Server)
        POPULATEAddressSpace.__init__(self, self.Server)
        FINDNodeID.__init__(self, self.CICs, self.Bus, self.Mops)
        self.endpoint = endpoint
        self.namespace = namespace

        self.logger = logging.getLogger('mopshub_log.crate')
        self._logger: Logger = logging.getLogger('asyncua')
        self._logger.setLevel(logging.WARNING)

        logging.basicConfig(level=logging.DEBUG)

    async def init(self, config_file: str, can_config_file: str, directory: str):
        """Setup the server and populate the address space
        :type config_file: str
        :param config_file: Configuration YAML containing active MOPS and custom init values, converter, aliases, etc.
        :type can_config_file: str
        :param can_config_file: Configuration YAML containing the settings of the CAN interfaces
        :type directory: str
        :param directory: Directory of the YAML configuration file for the CAN interfaces
        :rtype: None
        """

        await self.Server.init()
        self.Server.set_endpoint(self.endpoint)
        self.idx = await self.Server.register_namespace(self.namespace)
        await self.populate(config_file, can_config_file, directory)

    async def write_pe_status(self, cic_id, bus_id, status: str):
        for entry in self.server_dict:
            if f"CIC {cic_id}" in entry:
                if f"CANBus {bus_id}" in self.server_dict[entry]:
                    if f"PE Signal CANBus {bus_id}" in self.server_dict[entry][f"CANBus {bus_id}"]:
                        try:
                            node = (self.server_dict[entry][f"CANBus {bus_id}"][f"PE Signal CANBus {bus_id}"]
                                    ["Current Status"])
                            await node.write_value(status)
                        except KeyError as e:
                            self.logger.error(e)

    async def write_mops_mon(self, cic_id: int, bus_id: int, node_id: int, channel_name: str, adc_value: int):
        for entry in self.server_dict:
            if f"CIC {cic_id}" in entry:
                if f"CANBus {bus_id}" in self.server_dict[entry]:
                    if f"MOPS {node_id}" in self.server_dict[entry][f"CANBus {bus_id}"]:
                        try:
                            node = (self.server_dict[entry][f"CANBus {bus_id}"][f"MOPS {node_id}"]["MOPSMonitoring"]
                                    [channel_name])
                            await node.write_value(adc_value)
                        except KeyError as e:
                            self.logger.error(e)

    async def write_mops_adc(self, cic_id: int, bus_id: int, node_id: int, adc_index: int, adc_value: int):
        for entry in self.server_dict:
            if f"CIC {cic_id}" in entry:
                if f"CANBus {bus_id}" in self.server_dict[entry]:
                    if f"MOPS {node_id}" in self.server_dict[entry][f"CANBus {bus_id}"]:
                        if f"ADCChannel {adc_index:02}" in self.server_dict[entry][f"CANBus {bus_id}"][f"MOPS {node_id}"]:
                            try:
                                node = (self.server_dict[entry][f"CANBus {bus_id}"][f"MOPS {node_id}"]
                                        [f"ADCChannel {adc_index:02}"]["monitoringValue"])
                                await node.write_value(adc_value)
                            except KeyError as e:
                                self.logger.error(e)

    async def write_cic_adc(self, cic_id: int, bus_id: int, adc_index: int, adc_value: int):
        for entry in self.server_dict:
            if f"CIC {cic_id}" in entry:
                if f"CANBus {bus_id}" in self.server_dict[entry]:
                    try:
                        node = (self.server_dict[entry][f"CANBus {bus_id}"][f"ADC CANBus {bus_id}"]
                                [f"ADCChannel {adc_index:02}"]["monitoringValue"])
                        await node.write_value(adc_value)
                    except KeyError as e:
                        self.logger.error(e)

    async def write_mops_conf(self, cic_id: int, bus_id: int, node_id: int, index: str, value: int):
        for entry in self.server_dict:
            if f"CIC {cic_id}" in entry:
                if f"CANBus {bus_id}" in self.server_dict[entry]:
                    if f"MOPS {node_id}" in self.server_dict[entry][f"CANBus {bus_id}"]:
                        try:
                            node = (self.server_dict[entry][f"CANBus {bus_id}"][f"MOPS {node_id}"]["MOPSInfo"]
                                    [index])
                            await node.write_value(str(value))
                        except KeyError as e:
                            self.logger.error(e)

    async def __aenter__(self):
        """Start server when entering a context.
        :rtype: None
        """
        await self.Server.start()

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None):
        """Stop server when exiting a context.
        :rtype: None
        """
        await self.Server.stop()
