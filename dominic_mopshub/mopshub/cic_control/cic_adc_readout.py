import time
from random import randint
import logging

try:
    import spidev
except Exception as e:
    logging.exception(e)
    logging.warning('spidev could not be imported')

from additional_scripts import logger_setup
from hardware_control.multiplexer_config import MPconfig


class CICreadout(MPconfig):
    """
    This class is going to readout the ADC on the CIC Card.
    Which CIC card and which Bus can be defined through the configuration of the address bits in MPconfig
    """

    def __init__(self):
        # As Channel 4-7 all connected to the same net (GND) the actual read address list only captures Channel 0-4
        MPconfig.__init__(self)
        self.channel_value = ("UH", "UL", "VCAN-MOPS", "Temperature", "IMON1", "IMON2")
        self.__address_byte = (0x00, 0x08, 0x10, 0x18, 0x20, 0x28)
        self.__bus = 1

        self.logger = logging.getLogger('mopshub_log.cic_adc_readout')

    def read_adc(self, device, mp_channel, can_interface):
        self.logger.info(f'CIC ADC Readout Channel {mp_channel}')
        self.mp_switch(mp_channel, can_interface)
        spi = spidev.SpiDev()
        # important !!!! device 0 corresponds to can_interface 1
        # important !!!! device 1 corresponds to can_interface 0
        try:
            spi.open(self.__bus, device)
            spi.max_speed_hz = 5000
            self.logger.info(f'Connected successful to SPI Bus {self.__bus} Device {device}')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'Can not open connection to SPI Bus {self.__bus} Device {device}')
            return None

        msg_out = [self.__address_byte[0], 0,
                   self.__address_byte[1], 0,
                   self.__address_byte[2], 0,
                   self.__address_byte[3], 0,
                   self.__address_byte[4], 0,
                   self.__address_byte[5], 0,
                   0, 0]
        try:
            adc_read = spi.xfer2(msg_out)
            time.sleep(0.5)
            self.logger.info(f'Reading CIC-ADC on Channel {mp_channel} on CAN {can_interface}')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'An Error occurred while reading out CIC-ADC on '
                              f'Channel {mp_channel} on CAN {can_interface}')
            return None

        time.sleep(0.05)
        adc_result = []
        result1 = ((int(adc_read[(0 * 2) + 2]) * 256 + int(adc_read[(0 * 2) + 3])) * 0.7568) / 1000
        result2 = ((int(adc_read[(1 * 2) + 2]) * 256 + int(adc_read[(1 * 2) + 3])) * 0.7568) / 1000
        IMON1 = round(result1-result2, 4)
        adc_result.append(IMON1)
        for i in range(2, len(self.__address_byte)):
            result = ((int(adc_read[(i * 2) + 2]) * 256 + int(adc_read[(i * 2) + 3])) * 0.7568) / 1000
            result = round(result, 4)
            adc_result.append(result)
        spi.close()
        self.logger.info("ADC Read out finished")
        return adc_result

    # def dummy_read(self):
    #     # for testing
    #     result = []
    #     for i in range(0, len(self.__address_byte)):
    #         result.append(randint(0, 100))
    #     self.logger.info('ADC CIC readout finished')
    #     return result
