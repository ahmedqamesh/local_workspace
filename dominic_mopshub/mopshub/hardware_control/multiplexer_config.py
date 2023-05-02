import time
import numpy as np
import logging

from additional_scripts import logger_setup

try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning('RPI GPIO could not be imported')


class MPconfig:
    """
    This class is going to handle everything related to the Multiplexer on the Mopshub-for beginners.
    The class should switch the data select inputs to the values corresponding to the current CAN channel.
    Without this functionality it is not possible to choose the right MOPS to talk to.
    """

    def __init__(self):
        self.__selA0 = 7
        self.__selA1 = 29
        self.__selA2 = 31
        self.__selB0 = 15
        self.__selB1 = 16
        self.__selB2 = 37

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(self.__selA0, GPIO.OUT)
        GPIO.setup(self.__selA1, GPIO.OUT)
        GPIO.setup(self.__selA2, GPIO.OUT)

        GPIO.setup(self.__selB0, GPIO.OUT)
        GPIO.setup(self.__selB1, GPIO.OUT)
        GPIO.setup(self.__selB2, GPIO.OUT)

        """
        A and B are related to different the two CAN channel CAN1 and CAN2
        It is important to not choose on both CAN channel the same Multiplexer channel as the signals than could
        be read on both.
        """
        # Format of switch Table: [MPchannel, A0/B0, A1/B1, A2/B2]
        self.__switch_table = np.array([[0, 0, 0],
                                        [1, 0, 0],
                                        [0, 1, 0],
                                        [1, 1, 0],
                                        [0, 0, 1],
                                        [1, 0, 1],
                                        [0, 1, 1],
                                        [1, 1, 1]])

        self.logger = logging.getLogger('mopshub_log.multiplexer')

    def mp_switch(self, mp_channel, can_channel):
        if mp_channel is None or can_channel is None:
            self.logger.error('Missing Parameter. Can not switch MP channels')
            return 0

        if mp_channel in range(0, 8):
            __mp_channel = mp_channel
        elif mp_channel in range(25, 33):
            table_offset = 25
            __mp_channel = mp_channel - table_offset
        else:
            return 0

        # indexing of switch table: [y][x]
        # This needs to be improved and is not working with the cic readout at the moment!!!!!!
        try:
            if can_channel == 1:
                GPIO.output(self.__selA0, int(self.__switch_table[__mp_channel][0]))
                GPIO.output(self.__selA1, int(self.__switch_table[__mp_channel][1]))
                GPIO.output(self.__selA2, int(self.__switch_table[__mp_channel][2]))
                self.logger.info('MP Channel was set to Channel %s with A0 = %s, A1 = %s, A2 = %s', mp_channel,
                                 self.__switch_table[__mp_channel][0], self.__switch_table[__mp_channel][1],
                                 self.__switch_table[__mp_channel][2])
                return True

            if can_channel == 0:
                GPIO.output(self.__selB0, int(self.__switch_table[__mp_channel][0]))
                GPIO.output(self.__selB1, int(self.__switch_table[__mp_channel][1]))
                GPIO.output(self.__selB2, int(self.__switch_table[__mp_channel][2]))
                self.logger.info('MP Channel was set to Channel %s with B0 = %s, B1 = %s, B2 = %s', mp_channel,
                                 self.__switch_table[__mp_channel][0], self.__switch_table[__mp_channel][1],
                                 self.__switch_table[__mp_channel][2])
                return True
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'Some ERROR occurred while setting MP Channel {mp_channel}')
