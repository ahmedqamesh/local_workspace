########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.01.2022
"""
########################################################

import binascii
import os
import serial
from serial.tools import list_ports
import time
import numpy as np
from clint.textui import colored
try:
    from logger_main   import Logger
except (ImportError, ModuleNotFoundError):
    from .logger_main   import Logger
import sys   
import logging
import re
import subprocess
timeout = 0.05
log_format = '%(log_color)s[%(levelname)s]  - %(name)s -%(message)s'
log_call = Logger(log_format = log_format,name = "Serial Debug",console_loglevel=logging.INFO, logger_file = False)


class SerialServer(serial.Serial):

    def __init__(self, port=None, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,device = None, timeout=1):
        self.logger = log_call.setup_main_logger()
        #self.logger.info(f'Serial Settings : Port{port}, baudrate {baudrate}')
        port_detected = self.get_serial_port(device)
        if port_detected : port = port_detected[0]
        else: port = port
        try:
            super().__init__(port=port, baudrate=baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                             stopbits=serial.STOPBITS_ONE, timeout=timeout) 
            self.resetServer()
        except Exception as e : 
            ports_return = self.list_available_ports(msg = None)
            self.logger.error(f'Port{port} is not activated, The following ports are available {ports_return}')
            self.list_available_ports(msg = True)
            sys.exit(1)
        self.__bytes_written = 0
    
    def resetServer(self):        
        # Read and discard any existing data in the buffer
        self.reset_input_buffer()
        
        # Optionally, you can also clear the output buffer
        self.reset_output_buffer()

     
    def list_available_ports(self,msg = True):
        ports = serial.tools.list_ports.comports()
        ports_return = []
        for port in ports:
            ports_return.append(port.device)
            
            if msg:  self.logger.info(f'Port : {port.device} - {port.description} - {port.manufacturer} - {port.serial_number}')
        return ports_return

    def openServer(self):
        if not self.isOpen():
            self.open()
            
    def closeServer(self):
        if self.open():
            # Destructor, close port when serial port instance is freed
            self.__del__()
    def rx_data(self):
       #Byte = self.readline()
        return self.read() #read one byte
    
    
    def tx_data(self, data):
        self.openServer()
        #ser.write('6'.encode())
        self.__bytes_written = self.write(data)

    def bytes_written(self):
        return self.__bytes_written

    def read_full_line(self):
        line = b''
        while True:
            char = self.read(1)
            if char == b'\n':
                break
            line += char
        return line.decode().strip()


    def get_serial_port(self, vid_pid):
        ##
        # @return Array of compatible serial ports
        # @param vid_pid Vendor id, can be obtained via lsusb
        #
        # Provides all serial ports with vid_pid
        # Exits if no mathich port is found
        #
    
        list_ports.comports()
        temp = list(list_ports.grep(vid_pid))
        ports = []
        if(len(temp) == 0):
            self.logger.error('No matching USB device (' + colored.blue(vid_pid) + ') found!. Please check if Arty board is connected.')
        else:
            #self.logger.status('Found {:d} possible USB deivces'.format(len(temp)))
            for n in range(len(temp)):
                self.logger.status('Detect USB device ' + colored.blue(vid_pid) + ' at ' + colored.yellow(temp[n][0]))
                ports.append(temp[n][0])
        return ports


    def list_usb_ports(self):
        device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        df = subprocess.check_output("lsusb")
        devices = []
        for i in df.split(b'\n'):
            if i:
                info = device_re.match(i)
                if info:
                    dinfo = info.groupdict()
                    dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                    devices.append(dinfo)
                    print(dinfo)
