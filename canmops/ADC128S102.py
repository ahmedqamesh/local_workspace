#!/usr/bin/env python
#https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-2-play-sounds
# Bitbang'd SPI interface with an ADC128S102 ADC device
# ADC128S102 is 8-channel 120-bit analog to digital converter
#  Connections are:
#     VDGND[P12]=> GND  [p20] 
#     VD   [P13]=> 3.3V [p17]
#     DIN  [P14]=> MOSI [P19] 24
#     DOUT [P15]=> MISO [P21] 23         
#     CLK  [P16]=> SCLK [p23] 18 
#               => VREF 
#     CS   [P1 ]=> CE0  [p24] 25
#     VA   [P2 ]=> 3.3V [p1 ] 
#     VAGND[P3 ]=> GND  [p6 ] 
#               => AIN[P4-11]

import time
import sys
import spidev


spi_ch = 0 #corresponds to CS0

# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

def read_adc(adc_ch, vref = 3.3):

    # Make sure ADC channel is 0 or 1
    #if adc_ch != 0:
    #    adc_ch = 1

    # Construct SPI message
    #  0, 1, 2, 6, 7 bits are (don't care): Logic low (0)
    #  3,4,5 bit (ADD): 111 to select channels 0-7 and here I am choosing 0
    msg = 0b0
    msg = ((msg << 1) + adc_ch) << 3
    msg = [msg, 0b00]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n

    # Calculate voltage form ADC value
    voltage = (vref * adc)/ 4096

    return voltage

# Report the channel 0 and channel 1 voltages to the terminal
try:
    while True:
        i = 4
        adc = read_adc(i)
        #adc_1 = read_adc(1)
        print("Ch",i,":", round(adc, 2), "V")
        time.sleep(0.2)

finally:
    GPIO.cleanup()