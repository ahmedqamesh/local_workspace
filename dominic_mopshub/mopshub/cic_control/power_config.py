import logging
import time

from additional_scripts import logger_setup
from hardware_control.multiplexer_config import MPconfig

try:
    import RPi.GPIO as GPIO
    import spidev
except ImportError:
    logging.error(ImportError)
    logging.warning('RPI GPIO could not be imported')


class PEconfig(MPconfig):

    def __init__(self):
        self.__CE = 36
        self.__Data = 32
        self.__Res = 33

        self.__bus = 1

        MPconfig.__init__(self)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(self.__CE, GPIO.OUT)
        GPIO.setup(self.__Data, GPIO.OUT)
        GPIO.setup(self.__Res, GPIO.OUT)

        # self.power_off_table = [1, 1, 1, 1, 1, 1, 0, 1]
        self.locked_by_user = [False for _ in range(8)]
        self.locked_by_sys = [False for _ in range(8)]
        self.current_status_table = [0, 0, 0, 0, 0, 0, 0, 0]

        self.logger = logging.getLogger('mopshub_log.power_enable_config')

    def set_power_off(self):
        for i in range(0, len(self.current_status_table)):
            self.power_off(i)

    def reset_mode(self):
        try:
            GPIO.output(self.__Res, GPIO.LOW)
            GPIO.output(self.__CE, GPIO.HIGH)
            self.logger.info('Latch was reseted')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error('Some Error occurred while resetting Latch')

    def addressable_latch_mode(self, channel, data):
        try:
            GPIO.output(self.__Res, GPIO.HIGH)
            GPIO.output(self.__CE, GPIO.LOW)
            self.logger.info('Latch is now in the addressable latch mode')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error('Some Error occurred while activating addressable latch mode')

        if channel in range(0, 8):
            __channel = channel
        elif channel in range(25, 33):
            table_offset = 25
            __channel = channel - table_offset
        else:
            self.logger.error(f'Could not identify channel {channel}')
            return 0

        mp = self.mp_switch(__channel, 1)
        if mp is True:
            try:
                GPIO.output(self.__Data, int(data))
            except Exception as e:
                self.logger.error(f"Error while writing Data to Latch: {e}")

    def memory_mode(self):
        try:
            GPIO.output(self.__Res, GPIO.HIGH)
            GPIO.output(self.__CE, GPIO.HIGH)
            self.logger.info('Latch is now in the memory mode')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error('Some Error occurred while activating memory mode')

    def demultiplexer_mode(self):
        try:
            GPIO.output(self.__Res, GPIO.LOW)
            GPIO.output(self.__CE, GPIO.LOW)
            self.logger.info('Latch is now in the demultiplexer mode')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error('Some Error occurred while activating demultiplexer mode')

    def check_status(self, channel):
        if channel in range(0, 8):
            __channel = channel
        elif channel in range(25, 33):
            table_offset = 25
            __channel = channel - table_offset
        else:
            self.logger.error(f'Could not identify channel {channel}')
            return 0

        return self.current_status_table[__channel], self.locked_by_sys[__channel], self.locked_by_user[__channel]

    def power_on(self, channel, set_flag=None):

        spi = spidev.SpiDev()
        try:
            spi.open(self.__bus, 0)
            spi.max_speed_hz = 5000
            self.logger.info(f'Connected successful to SPI Bus {self.__bus} Device 0')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'Can not open connection to SPI Bus {self.__bus} Device 0')
            return None

        if channel in range(0, 8):
            __channel = channel
        elif channel in range(25, 33):
            table_offset = 25
            __channel = channel - table_offset
        else:
            self.logger.error(f'Could not identify channel {channel}')
            return 0

        try:
            if bool(self.locked_by_sys[__channel]) is False:
                if bool(self.locked_by_user[__channel]) is False or set_flag is not None:
                    try:
                        spi.writebytes([0xFF])
                    except Exception as e:
                        self.logger.exception(e)
                    self.addressable_latch_mode(channel, 1)
                    time.sleep(0.0001)
                    self.addressable_latch_mode(channel, 0)
                    time.sleep(0.0001)
                    self.current_status_table[__channel] = 1
                    if set_flag is not None:
                        self.locked_by_user[__channel] = set_flag
                    self.logger.info(f"Power Channel {__channel} is now ON")
                    print(f"Power Channel {__channel} is now ON")
                    return 1
                else:
                    self.logger.error(f'Power of Channel {__channel} was locked by user')
            else:
                self.logger.error(f'Power of Channel {__channel} was locked by sys while start up')
        except Exception as e:
            self.logger.exception(e)
            return None

    def power_off(self, channel, set_flag=None):

        spi = spidev.SpiDev()
        try:
            spi.open(self.__bus, 0)
            spi.max_speed_hz = 5000
            self.logger.info(f'Connected successful to SPI Bus {self.__bus} Device 0')
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f'Can not open connection to SPI Bus {self.__bus} Device 0')
            return None

        if channel in range(0, 8):
            __channel = channel
        elif channel in range(25, 33):
            table_offset = 25
            __channel = channel - table_offset
        else:
            self.logger.error(f'Could not identify channel {channel}')
            return 0

        try:
            if bool(self.locked_by_sys[__channel]) is False:
                if bool(self.locked_by_user[__channel]) is False or set_flag is not None:
                    try:
                        spi.writebytes([0x00])
                    except Exception as e:
                        self.logger.exception(e)
                    self.addressable_latch_mode(channel, 1)
                    time.sleep(0.0001)
                    self.addressable_latch_mode(channel, 0)
                    time.sleep(0.0001)
                    self.current_status_table[__channel] = 0
                    if set_flag is not None:
                        self.locked_by_user[__channel] = set_flag
                    self.logger.info(f"Power Channel {__channel} is now OFF")
                    print(f"Power Channel {__channel} is now OFF")
                    return 0
                else:
                    self.logger.error(f'Power of Channel {__channel} was locked by user')
            else:
                self.logger.error(f'Power of Channel {__channel} was locked by sys while start up')
        except Exception as e:
            self.logger.exception(e)
            return None


power_signal = PEconfig()
