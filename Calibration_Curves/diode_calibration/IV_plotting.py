#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#
import time
import threading
import numpy as np
from numpy import std
import tables as tb
import csv
import logging
from tables import *
import pandas as pd
import matplotlib.pyplot as plt

def Plotting_IV_test(diodes=[0]):
    fig = plt.figure()
    fig.add_subplot(111)
    ax = plt.gca()
    conversion = 10**9
    for diode_id in diodes:
        with tb.open_file("IV_"+diode_id+".h5", 'r') as in_file:
            IV_results = in_file.root.IV_results[:]
            v=IV_results['voltage']
            mean = IV_results['mean_current']*conversion
            std =IV_results['std_current']*conversion
        ax.errorbar(v,mean,yerr=std, 
                        fmt='o', color=colors[diodes.index(diode_id)], markersize=5, 
                        ecolor="black",label=("Diode %s " % diode_id))
        ax.plot(v,mean,color='black')
        print "loading diode", diode_id
    plt.legend(loc = "upper right")
    plt.ylim(-1, 15)
    #plt.xlim(0,52)
    #ax.set_xscale('log')
    plt.xlabel("Reverse Voltage [V]")
    plt.ylabel("Current [nA]")
    plt.title('IV_Curve')
    plt.savefig("IV_"+diode_id+ ".png")
    plt.show()
    
def Plotting_IV_test_old(diodes=[0],colors=None):
    fig = plt.figure()
    fig.add_subplot(111)
    ax = plt.gca()
    conversion = 10**9
    for diode_id in diodes:
        v = []
        mean = []
        std = []
        with open("IV_"+diode_id+".csv", 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            reader.next()
            for row in reader:
                v = np.append(v, float(row[2]))
                mean = np.append(mean, float(row[1])*conversion)
                std = np.append(std, float(row[3])*conversion)*1.04
            ax.errorbar(v[5:],mean[5:],yerr=std[5:], 
                        fmt='o', color=colors[diodes.index(diode_id)], markersize=5, 
                        ecolor="black",label=("Diode %s " % diode_id))
            ax.plot(v,mean,color='black')
        print "loading diode", diode_id
    plt.legend()
    #ax.set_xscale('log')
    #ax.set_yscale('log')
    
    plt.ylim(-1.5,0)
    plt.xlim(-52,1)

    plt.xlabel("Reverse Voltage [V]")
    plt.ylabel("Current [nA]")
    plt.title('IV Curves for the diodes under calibration')
    plt.savefig("IV_curve.png")
    plt.show()
    
if __name__ == '__main__':
    colors = [ '#006381','red',  '#33D1FF','#F5A9BC', 'grey', '#7e0044', 'orange', "maroon", 'green', "magenta"]
    Plotting_IV_test(diodes=["A","B","C"])
    Plotting_IV_test_old(diodes=["1","2","3"],colors=colors)