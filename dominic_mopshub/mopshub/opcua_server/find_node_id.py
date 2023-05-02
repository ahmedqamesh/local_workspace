import logging
import sys
from asyncua import Node
import collections

from additional_scripts import logger_setup

sys.path.insert(0, "../..")


class FINDNodeID:

    def __init__(self, cics, bus, mops):
        self.CICs = cics
        self.Bus = bus
        self.Mops = mops

        self.logger = logging.getLogger('mopshub_log.crate')
        self._logger: Logger = logging.getLogger('asyncua')
        self._logger.setLevel(logging.DEBUG)

    async def find_object(self, search_string: str) -> Node:
        """Find a server object in the node tree. Objects have to exist, otherwise a KeyError exception is raised.

        :param search_string: Search string (e.g "CIC 2:MOPS 1:ADCChannel 01")
        :return:
        """

        def error(issue):
            """Raise a KeyError exception
            :param issue: The Key that was unable to match
            """
            self._logger.error(f"Invalid key {issue} in {search_string}")
            raise KeyError(f"Invalid key {issue}")

        async def is_string(node: Node, string: str) -> bool:
            """Check if the node name matches to a search string
            :rtype: bool
            :type node: asyncua Node
            :type string: str
            :param node: The node to be search for the pattern
            :param string: The pattern to match
            :return: True if the pattern is in the browse name, else False
            """
            return string in (await node.read_browse_name()).__str__()

        search = search_string.split(":")

        # Searching the right CIC card
        cic_search = search[0]
        if "CIC" not in cic_search:
            error({cic_search})
        cic_index = int(cic_search.replace("CIC", ""))
        if self.CICs[cic_index] is None:
            error({cic_search})
        cic = self.CICs[cic_index]
        if len(search) == 1:
            return cic

        # Searching the Bus:
        bus_search = search[1]
        if "CANBus" not in bus_search:
            error({bus_search})
        bus_index = int(bus_search.replace("CANBus", "")) - 1
        if self.Bus[bus_index] is None:
            error({bus_search})
        bus = self.Bus[bus_index]
        if len(search) == 2:
            return bus

        # Searching the specific Mops on the Bus
        if "MOPS" in search[2]:
            mops_search = search[2]
            mops_index = int(mops_search.replace("MOPS", ""))
            mops = None

            if collections.Counter(self.Mops[bus_index])[None] == len(self.Mops[bus_index]):
                self.logger.error("On Bus %s is no Mops registered", bus)
                return error({mops_search})
            else:
                for entry in self.Mops[bus_index]:
                    if entry is not None:
                        children = await entry.get_children()
                        for child in children:
                            desc = await child.read_description()
                            if desc.Text == 'NodeID':
                                node_id = await child.get_value()
                                if node_id == mops_index:
                                    mops = entry
                                    break

            # Searching the specific Node of the specific Channel
            channel_search = search[3]
            if mops is not None:
                if len(search) == 3:
                    return mops
                if len(search) == 4:
                    adc_channel = [node for node in await mops.get_children() if (await is_string(node, channel_search))]
                    if not len(adc_channel) == 1:
                        error({channel_search})
                    else:
                        return adc_channel[0]
            else:
                self.logger.error('Mops /" %s /" could not be found', mops_search)
                return error({mops_search})

            error(search)

        elif "ADC CANBus" in search[2]:
            adc_search = search[2]
            channel_search = search[3]
            adc_object = [node for node in await bus.get_children() if (await is_string(node, adc_search))]
            if not len(adc_object) == 1:
                error({adc_search})
            cic_adc = adc_object[0]
            adc_channel = [node for node in await cic_adc.get_children() if (await is_string(node, channel_search))]
            if not len(adc_channel) == 1:
                error({channel_search})
            return adc_channel[0]

        elif "PE Signal CANBus" in search[2]:
            pe_search = search[2]
            pe_object = [node for node in await bus.get_children() if (await is_string(node, pe_search))]
            return pe_object[0]

        else:
            error({search[2]})

    async def find_in_node(self, node: Node, search_string: str):
        """Search for a variable by name in a node
        :type node: asyncua Node
        :type search_string: str
        :param node: Node that contains the variable
        :param search_string: Part of the variable name
        :return: Array of all variables that matched to the search string
        """

        async def is_string(node, string):
            return string in (await node.read_browse_name()).__str__()

        return [v for v in (await node.get_variables()) if (await is_string(v, search_string))]
