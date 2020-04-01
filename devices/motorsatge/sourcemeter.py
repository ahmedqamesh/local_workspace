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

    def IV_test(self, CurrentLimit=1.000000E-01, start_V=False, step_V=False, end_V=False,
                Itterations=False, Stat_Delay=False, Plot=False, chip_num=True):
        self.write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", self.ask("SENS:CURR:PROT?")
        self.write(":SOUR:FUNC VOLT")
        # To save data as HDF5
        File = tb.open_file('/home/silab62/MasterWork/' + str(chip_num) + ".h5", 'w')
        description = np.zeros((1,), dtype=np.dtype([("Voltage", "f8"), ("Mean_Current", "f8"), ("std_Current", "f8"), ("Current", "f8")])).dtype
        table1 = File.create_table(File.root, name='IV_Results', description=description)
        table1.flush()
        row = table1.row
        Voltage_array = []
        mean_array = []
        std_array = []
        logging.info("Start taking Data")
        for i in range(start_V, end_V + step_V, step_V):
            self.write(':SOUR:VOLT ' + str(i))
            #self.write(":SOUR:DEL "+str(Delay))
            current_array = []
            for j in range(Itterations):
                if Stat_Delay:
                    time.sleep(Stat_Delay)
                val = self.ask(":MEAS:CURR?")
                current = float(val[14:-43])
                current_array.append(current)
                mean = np.mean(current_array)
                std = np.std(current_array)
            print "Voltage = ", i, "", "Current = ", current_array, "", "Mean current = ", mean, "", "Error = ", std
            row["Voltage"] = i
            row["Mean_Current"] = mean
            row["Current"] = current
            row["std_Current"] = std
            row.append()
            mean_array.append(mean)
            std_array.append(std)
            Voltage_array.append(i)
        # print mean_array , std_array, Voltage_array
        File.close()
        logging.info("Start creating Tables table")
        df = pd.DataFrame({"Voltage": Voltage_array, "Mean_Current": mean_array, "std_Current": std_array})
        df.to_csv('/home/silab62/MasterWork/' + str(chip_num) + ".CSV", index=True)
        if Plot:
            self.Plotting_IVcurve_Stat(Directory='/home/silab62/MasterWork/', h5=True, Multiple=True)

    def Plotting_IVcurve_Stat(self, Directory=False, h5=False, Multiple=True):
        meas_curr = []
        meas_stdcurr = []
        meas_volt = []
        curr_min = []
        curr_max = []
        if h5:
            plot_min = []
            for chip_num in range(1, 4, 1):
                with tb.open_file(Directory + str(chip_num) + ".h5", 'r') as in_file:
                    IV_Results = in_file.root.IV_Results[:]
                    curr_min = np.append(curr_min, np.min(IV_Results['Mean_Current']))
                    plot_min = np.append(plot_min, min(curr_min))
                    plt.errorbar(IV_Results['Voltage'], IV_Results['Mean_Current'] * 1e9, fmt='o', marker='o',
                                 label=("Diode %s " % str(chip_num)), yerr=IV_Results['std_Current'] * 5e10)
                print "finished load for chip", chip_num
            plt.legend()
            plt.ylim(min(plot_min) * 1e10 / 5, 1)
            plt.xlabel("Negative Voltage (V)")
            plt.ylabel("Current (nA)")
            plt.title('IV_Curve')
            plt.savefig('/home/silab62/MasterWork/IV_table_h5.png')
            plt.show()

        else:
            plot_min = []
            for chip_num in range(1, 3, 1):
                with open(Directory + str(chip_num) + ".csv", 'rb') as in_file_csv:
                    reader = csv.reader(in_file_csv, delimiter=',')
                    for i in range(0, 1):  # To ignore the first row
                        next(reader)
                    for row in reader:
                        meas_curr = np.append(meas_curr, float(row[1]))
                        meas_volt = np.append(meas_volt, float(row[2]))

                        meas_stdcurr = np.append(meas_stdcurr, float(row[3]))
                        curr_min = np.append(curr_min, np.min(meas_curr))
                        curr_max = np.append(curr_max, np.max(meas_curr))
                    print "finished load for chip", chip_num
                    plot_min = np.append(plot_min, min(curr_min))
                    plt.errorbar(meas_volt, meas_curr * 1e9, fmt='o', marker='o', label=("Chip %s Average" % str(chip_num)), yerr=meas_stdcurr * 1e11)
            plt.legend()
            plt.ylim(min(plot_min) * 1e10 / 5, 1)
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current (A)")
            plt.title('IV_Curve')
            plt.savefig('/home/silab62/MasterWork/IV_table_csv.png')
            plt.show()

    def Run_Sourcemeter(self, CurrentLimit=1.000000E-01, BiasedVolt=20):
        self.write(":OUTP ON")
        self.write("*RST")
        self.write(":SOUR:VOLT:RANG 60")
        self.write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", self.ask("SENS:CURR:PROT?")
        self.write(":SOUR:FUNC VOLT")
        self.write(':SOUR:VOLT ' + str(BiasedVolt))
