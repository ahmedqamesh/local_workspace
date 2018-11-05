#
# ------------------------------------------------------------
# Copyright (c) SILAB , Physics Institute of Bonn University
# ------------------------------------------------------------
#
from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.backends.backend_pdf import PdfPages
import csv

Energy = []
Counts = []
with open("/home/silab62/git/XrayMachine_Bonn/Calibration_Curves/Bonn/Simulation/Siemens_Simulation/Tungsten_40KeV.csv", 'r')as parameters:  # Get Data for the first Voltage
    reader = csv.reader(parameters)
    reader.next()
    for row in reader:
        Energy = np.append(Energy, float(row[0]))
        Counts = np.append(Counts, int(float(row[1])))
    x = np.repeat(Energy,Counts)
    #print Energy
    ax = plt.gca()
    plt.plot(Energy, Counts,color='#0504aa')
    ax.set_xscale('log')
    #n, bins, patches = plt.hist(x=x, bins='auto', color='#0504aa', rwidth=0.85)
    ax.legend()
    plt.show()

    