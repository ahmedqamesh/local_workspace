#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#
from basil.dut import Dut
import time
import numpy as np
import tables as tb
import csv
import logging
from tables import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
from matplotlib.backends.backend_pdf import PdfPages
from Tkinter import *

def temprature_dose(Directory=False, Sourcemeter=True,time_size=100,delay=2, CurrentLimit=1.000000E-06):
    '''
    Assuming that the cabinet door is the -z
    x : Number of movements to x direction 
    z: Number of movements inside the cabinet
    Size_x: size of the steps in x direction
    '''
    t0 = time.time()
    if Sourcemeter:
        dut = Dut('sensor_sourcemeter_scan_pyserial.yaml')
        dut.init()
        dut['sm'].write(":OUTP ON")
        dut['sm'].write("*RST")
        dut['sm'].write(":SOUR:VOLT:RANG 60")
        dut['sm'].write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", dut['sm'].ask("SENS:CURR:PROT?")
        dut['sm'].write(":SOUR:FUNC VOLT")
        dut['sm'].write(':SOUR:VOLT 50')
    else:
        dut = Dut('temprature_scan_pyserial.yaml')
        dut.init()
    with tb.open_file(Directory +'temprature_dose.h5', "w") as out_file_h5:
        description = np.zeros((1,), dtype=np.dtype([("time", "f8"),("current", "f8"), ("temprature", "f8"),("humidity", "f8"), ("dew", "f8")])).dtype
        Data_table = out_file_h5.create_table(out_file_h5.root, name='temprature_dose',
                                                      description=description,
                                                      filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
        read = Data_table.row
        for i in xrange(time_size):
            t1 = time.time() 
            read["time"] = t1 -t0
            read["temprature"] =dut['ts'].get_temperature()
            read["humidity"] = dut['ts'].get_humidity()
            read["dew"] = dut['ts'].get_dew_point()
            if Sourcemeter:
                val = dut['sm'].ask(":MEAS:CURR?")
                current = val[15:-43]
            else:
                current = random.randint(1, 101)
            read["current"] = current
            read.append()
            temp =dut['ts'].get_temperature()                        
            print  temp, t1 -t0 , current
            time.sleep(delay)
        Data_table.flush()
    out_file_h5.close()
'''
Note: Done forget to check the yaml file
'''
Directory = "/home/silab62/git/XrayMachine_Bonn/tools/temprature_sensor/"
temprature_dose(Directory=Directory)