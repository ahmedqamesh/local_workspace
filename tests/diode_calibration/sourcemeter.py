#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# ------------------------------------------------------------
#
import time
import threading
import numpy as np
from basil.HL.RegisterHardwareLayer import HardwareLayer
from numpy import std
import tables as tb
import csv
import logging
from tables import *
import pandas as pd
import matplotlib.pyplot as plt


class sourcemeter(HardwareLayer):
    '''Driver for  Sourcemeter 
    '''

    def __init__(self, intf, conf):
        super(sourcemeter, self).__init__(intf, conf)

    def write(self, value):
        self._intf.write(str(value))

    def read(self, command=None):
        answer = self._intf._readline()
        return answer

    def reset(self, Limit=False, LValue=0):
        if Limit:
            cmd = 'SENS:CURR:PROT ' + str(LValue)
            self.write(cmd)
            self.write("SENS:CURR:PROT?")
            print self.read()

    def ask(self, value):
        self._intf.write(str(value))
        answer = self._intf._readline()
        return answer

    def IV_test(self, Directory = None, CurrentLimit=1.000000E-01, start_V=False, step_V=False, end_V=False,
                Itterations=False, Stat_Delay=False, Plot=False, diodes=[0]):
        self.write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", self.ask("SENS:CURR:PROT?")
        self.write(":SOUR:FUNC VOLT")
        for diode_id in diodes:
            File = tb.open_file(Directory + "IV_"+diode_id+ ".h5", 'w')
            description = np.zeros((1,), dtype=np.dtype([("voltage", "f8"), ("mean_current", "f8"), ("std_current", "f8")])).dtype
            table1 = File.create_table(File.root, name='IV_results', description=description)
            table1.flush()
            row = table1.row
            Voltage_array = []
            mean_array = []
            std_array = []
            logging.info("Start taking Data")
            voltage_array = np.arange(start_V, end_V + step_V, step_V)
            length_v=len(voltage_array) 
            current_array = np.zeros(shape=(length_v, Itterations), dtype=np.float64)
            for i in np.arange(length_v):
                self.write(':SOUR:VOLT ' + str(voltage_array[i]))
                self.write(":SOUR:DEL 3")
                time.sleep(Stat_Delay)
                c_array = []
                for j in range(Itterations):
                    #time.sleep(Stat_Delay)
                    val = self.ask(":MEAS:CURR?")
                    current = val[15:-43]
                    c_array.append(float(current))
                    current_array[i,j] = float(current)
                mean = np.mean(c_array)
                std = np.std(c_array)
                print "Voltage = %0.2f"%voltage_array[i], "", "Mean current = ", mean, "", "Error = ", std
                row["voltage"] = voltage_array[i]
                row["mean_current"] = mean
                row["std_current"] = std
                row.append()
            File.create_array(File.root, 'current_array', current_array, "current_array")
            File.close()
            logging.info("Start creating table")
        if Plot:
            self.Plotting_IV_test(Directory=Directory,diodes=diodes)

    def Plotting_IV_test(self, Directory=False,diodes=[0]):
        fig = plt.figure()
        fig.add_subplot(111)
        ax = plt.gca()
        conversion = 10**9
        for diode_id in diodes:
            with tb.open_file(Directory + "IV_"+diode_id+".h5", 'r') as in_file:
                IV_results = in_file.root.IV_results[:]
                #curr_min = np.append(curr_min, np.min(IV_results['mean_current']))
                #plot_min = np.append(plot_min, min(curr_min))
            ax.errorbar(IV_results['voltage'], IV_results['mean_current']*conversion,yerr=IV_results['std_current']*conversion, 
                         fmt='o', color='black', markersize=0.9, ecolor='black',label=("Diode %s " % diode_id))
            print "loading diode", diode_id
        plt.legend(loc = "upper right")
        #plt.ylim(-6, 1)
        #plt.xlim(0,52)
        #ax.set_yscale('log')
        plt.xlabel("Reverse Voltage [V]")
        plt.ylabel("Current [nA]")
        plt.title('IV_Curve')
        plt.savefig(Directory+ "IV_"+diode_id+ ".png")
        plt.show()


    def Run_Sourcemeter(self, CurrentLimit=1.000000E-01, BiasedVolt=20):
        self.write(":OUTP ON")
        self.write("*RST")
        self.write(":SOUR:VOLT:RANG 60")
        self.write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", self.ask("SENS:CURR:PROT?")
        self.write(":SOUR:FUNC VOLT")
        self.write(':SOUR:VOLT ' + str(BiasedVolt))
