from additional_scripts import logger_setup
import logging
import re
import asyncio
import asyncua
import os
from yaml import dump


class BROWSEServer:
    def __init__(self, server):

        self.server = server
        self.crate_id = int
        self.can0_dict = {}
        self.can1_dict = {}
        self.server_dict = {}
        self.logger = logging.getLogger('mopshub_log.crate')

    async def browse_server(self):
        crate_id_var = await self.server.nodes.root.get_child(["0:Objects", "2:MOPSHUB Crate", "2:Crate ID"])
        self.crate_id = await crate_id_var.read_value()

        # configure_can0_obj = await self.server.nodes.root.get_child(["0:Objects", "2:MOPSHUB Crate", "2:Config CAN0"])
        # can0_var = await configure_can0_obj.get_variables()
        # methodes = await configure_can0_obj.get_methods()  # fixed endpoint
        # for methode in methodes:
        #     self.can0_dict["Configure CAN0"] = str(methode)
        # for node in can0_var:
        #     desc = await node.read_description()
        #     self.can0_dict[desc.Text] = str(node)
        # self.server_dict["Config CAN0"] = self.can0_dict

        # configure_can1_obj = await self.server.nodes.root.get_child(["0:Objects", "2:MOPSHUB Crate", "2:Config CAN1"])
        # can1_var = await configure_can1_obj.get_variables()
        # methodes = await configure_can1_obj.get_methods()  # fixed endpoint
        # for methode in methodes:
        #     self.can1_dict["Configure CAN1"] = str(methode)
        # for node in can1_var:
        #     desc = await node.read_description()
        #     self.can1_dict[desc.Text] = str(node)
        # self.server_dict["Config CAN1"] = self.can1_dict

        for cic_id in range(4):
            try:
                cic_card_obj = await self.server.nodes.root.get_child(
                    ["0:Objects", "2:MOPSHUB Crate", f"2:CIC {cic_id}"])
                bus_obj = await cic_card_obj.get_children()
                cic_dict = {}
                for bus in bus_obj:
                    bus_name = await bus.read_description()
                    bus_children = await bus.get_children()
                    bus_dict = {}
                    for children in bus_children:
                        children_desc = await children.read_description()
                        if "MOPS" in children_desc.Text:
                            grandchildren = await children.get_children()
                            adc_dict = {}
                            for grandchild in grandchildren:
                                grandchild_desc = await grandchild.read_description()
                                if "ADCChannel" in grandchild_desc.Text:
                                    channels = await grandchild.get_variables()
                                    channel_dict = {}
                                    for variable in channels:
                                        variable_desc = await variable.read_description()
                                        if variable_desc.Text == "monitoringValue":
                                            channel_dict[variable_desc.Text] = variable
                                        else:
                                            variable_value = await variable.read_value()
                                            channel_dict[variable_desc.Text] = variable_value
                                    adc_dict[grandchild_desc.Text] = channel_dict
                                elif "MOPSMonitoring" in grandchild_desc.Text:
                                    channels = await grandchild.get_variables()
                                    channel_dict = {}
                                    for variable in channels:
                                        variable_desc = await variable.read_description()
                                        channel_dict[variable_desc.Text] = variable
                                    adc_dict[grandchild_desc.Text] = channel_dict
                                elif "MOPSInfo" in grandchild_desc.Text:
                                    channels = await grandchild.get_variables()
                                    channel_dict = {}
                                    for variable in channels:
                                        variable_desc = await variable.read_description()
                                        channel_dict[variable_desc.Text] = variable
                                    adc_dict[grandchild_desc.Text] = channel_dict
                                elif "NodeID" in grandchild_desc.Text:
                                    node_id = await grandchild.read_value()
                                    adc_dict[grandchild_desc.Text] = node_id
                            bus_dict[children_desc.Text] = adc_dict
                        if "PE Signal CANBus" in children_desc.Text:
                            grandchildren = await children.get_children()
                            pe_dict = {}
                            for grandchild in grandchildren:
                                grandchild_desc = await grandchild.read_description()
                                if grandchild_desc.Text == "Description" or grandchild_desc.Text == "Bus ID":
                                    pe_dict[grandchild_desc.Text] = await grandchild.read_value()
                                else:
                                    pe_dict[grandchild_desc.Text] = grandchild
                            bus_dict[children_desc.Text] = pe_dict
                        if "ADC CANBus" in children_desc.Text:
                            grandchildren = await children.get_children()
                            adc_dict = {}
                            for grandchild in grandchildren:
                                grandchild_desc = await grandchild.read_description()
                                if "ADCChannel" in grandchild_desc.Text:
                                    channels = await grandchild.get_variables()
                                    channel_dict = {}
                                    for variable in channels:
                                        variable_desc = await variable.read_description()
                                        if variable_desc.Text == "monitoringValue":
                                            channel_dict[variable_desc.Text] = variable
                                        else:
                                            variable_value = await variable.read_value()
                                            channel_dict[variable_desc.Text] = variable_value
                                    adc_dict[grandchild_desc.Text] = channel_dict
                            bus_dict[children_desc.Text] = adc_dict
                        cic_dict[bus_name.Text] = bus_dict
                self.server_dict[f"CIC {cic_id}"] = cic_dict
            except Exception as e:
                self.logger.info(e)
