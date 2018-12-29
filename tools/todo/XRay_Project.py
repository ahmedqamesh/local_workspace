#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
from basil.dut import Dut
import random
import time
import numpy as np
from numpy import std
import tables as tb
import csv
import logging
from tables import *
import pandas as pd
import matplotlib.pyplot as plt
import os


def main():
    t0 = time.time()  # start time
    dut = Dut('mercury_pyserial.yaml')
    dut.init()
    t1 = time.time()  # end time

    File = tb.open_file('/home/silab62/MasterWork/' + "Project" + ".h5", 'w')
    description = np.zeros((1,), dtype=np.dtype([("x", "f8"), ("y", "f8"), ("z", "f8"), ("Distance", "f8"),
                                                 ("Temperature", "f8"), ("Humidity", "f8"), ("DEW", "f8")])).dtype
    table1 = File.create_table(File.root, name='IV_Results', description=description)
    table1.flush()
    row = table1.row
    for i in range(10):
        #vector1 = dut["MotorStage"].get_coordinates()
        #print vector1
        row["x"] = float(str(dut["MotorStage"].Read_Write("TP", address=1))[2:13])
        row["y"] = float(str(dut["MotorStage"].Read_Write("TP", address=2))[2:13])
        row["z"] = float(str(dut["MotorStage"].Read_Write("TP", address=3))[2:13])
        # time.sleep(1)

        #vector2 = dut["MotorStage"].get_coordinates()
        row["Distance"] = i  # dut["MotorStage"].get_Distance(vector1,vector2)
        row["Temperature"] = i  # dut["Thermohygrometer"].get_temperature()
        row["Humidity"] = i  # dut["Thermohygrometer"].get_humidity()
        row["DEW"] = i  # dut["Thermohygrometer"].get_dew_point()
        row.append()
    File.close()
#     with tb.open_file('/home/silab62/MasterWork/' + "Project" + ".h5", 'r') as in_file:
#         IV_Results = in_file.root.IV_Results[:]
#         plt.plot(IV_Results["Distance"], IV_Results["x"])
#     plt.xlabel("Negative Voltage (V)")
#     plt.ylabel("Current (nA)")
#     plt.title('IV_Curve')
#     plt.savefig('/home/silab62/MasterWork/project.png')
#     plt.show()
    print "Time Estimated = ", (t1 - t0)


if __name__ == '__main__':
    main()
