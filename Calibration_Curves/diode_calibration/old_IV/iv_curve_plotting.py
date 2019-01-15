'''
created by Daniel Coquelin Dec. 6, 2017
plotting of iv curves as measured using Keithley 2450 sourcemeter
data from csv files, more to be added from measurements with other sourcemeters

/home/daniel/MasterThesis/fe65_p2/iv_curves/8ch2defbuffer1.csv deleted due to bad measurement
'''
import numpy as np
import matplotlib.pyplot as plt
import logging
#from h5py.h5a import delete
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
import tables as tb
import yaml
import matplotlib as mpl
import matplotlib.mlab as mlab
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib import colors, cm
from scipy.stats import stats
from scipy.optimize import curve_fit
from math import ceil
import csv
import os
import pandas as pd

# in file data starts on line 8 (from 0)
# need columns (from 0) 1 (current) and 14 (voltage)
# want to read in all files from the folder, can select different ones later

def read_file(filename_csv):
    # may need the 'rb' option to read the file in binary
    with open('%s' % filename_csv, 'rb') as in_file_csv:
        reader = csv.reader(in_file_csv, delimiter=',')

        meas_curr = []
        meas_volt = []
        for i in range(0, 1):# To ignore the first row
            next(reader)
        for row in reader:            
            meas_volt = np.append(meas_volt, row[1])
            meas_curr = np.append(meas_curr, row[2])
        print ("completted file: %s" % filename_csv)
        in_file_csv.close()
    #print meas_curr, meas_volt     
    return meas_curr, meas_volt


def combine_and_plot(Directory=None):
    plot_min = []
    for chip_num in range(1, 4, 1):
        meas_curr = []
        meas_volt = []
        # want to read in all of the files here
        directory = os.path.join(Directory + str(chip_num))
        for root, dirs, files in os.walk(directory):
            for csv_file in files:
                if csv_file.endswith(".csv"):
                    hold1, hold2 = read_file(Directory+ str(chip_num)+"/"+str(csv_file))
                    meas_curr = np.append(meas_curr, hold1)
                    meas_volt = np.append(meas_volt, hold2)
                    
        print "finished load for chip", chip_num
        try: 
            meas_curr = meas_curr.astype(np.float)
            meas_volt = meas_volt.astype(np.float)
            curr_avg = []
            curr_min = []
            curr_max = []
            curr_err = []
            for vlt in xrange(0, -53, -1):
                curr_hold = np.mean(meas_curr[(meas_volt < (vlt + 0.9)) & (meas_volt >= (vlt - 1))])
                curr_avg = np.append(curr_avg, curr_hold)
                curr_err = np.append(curr_err, 1 / np.sqrt(len(meas_curr[(meas_volt < (vlt + 0.9)) & (meas_volt >= (vlt - 1))])))
                curr_hold = np.min(meas_curr[(meas_volt < (vlt + 0.9)) & (meas_volt >= (vlt - 1))])
                curr_min = np.append(curr_min, curr_hold)
                curr_hold = np.max(meas_curr[(meas_volt < (vlt + 0.9)) & (meas_volt >= (vlt - 1))])
                curr_max = np.append(curr_max, curr_hold)
                
            plt.errorbar(xrange(0, 53, 1), curr_avg* 1e9 , xerr=0., yerr=np.sqrt(curr_err)*0.5,
                         fmt='o', label=("Chip %s Average" % str(chip_num)))
            #plt.plot(xrange(0, -53, -1), curr_max * 1e9, label=("Chip %s Max" % str(chip_num)))
            #plt.plot(xrange(0, -53, -1), curr_min * 1e9, label=("Chip %s Min" % str(chip_num)))
            plot_min = np.append(plot_min, min(curr_min))  
            print chip_num          
        except:
            pass
    plt.legend()
    plt.ylim(min(plot_min)* 1e10/5, 1)    
    plt.xlabel("Negative Voltage (V)")
    plt.ylabel("Current (nA)")
    plt.title('IV_Curve')
    plt.savefig(Directory+'IV_Curve_Plotting.png') 
    plt.show()

def Plotting_IV_test(Directory=False,diodes=[0]):

    conversion = 10**9
    for diode_id in diodes:
	with tb.open_file(Directory + "IV_"+diode_id+".h5", 'r') as in_file:
		IV_results = in_file.root.IV_Results[:]
		plt.errorbar(IV_results['Voltage'], IV_results['Mean_Current']*conversion,yerr=IV_results['std_Current']*conversion, 
		             fmt='o', marker='o',markersize='1',#ecolor="black"
		             label=("Diode %s " % diode_id))
	    	print "finished loading diode", diode_id
	plt.legend(loc = "upper right")
	plt.ylim(-2,1)
	#plt.xlim(1,52)
	plt.xlabel("Negative Voltage [V]")
	plt.ylabel("Current [nA]")
	plt.title('IV_Curve')
	plt.savefig(Directory+ "IV_"+diode_id+".png")
	plt.show()



if __name__ == "__main__":
    Plotting_IV_test(Directory = "/home/silab62/git/XrayMachine_Bonn/tests/diode_calibration/old_IV/", diodes=["1","2","3"])
    #combine_and_plot(Directory = "/home/silab62/git/XrayMachine_Bonn/tests/diode_calibration/old_IV/")
    #read_file ("/home/silab62/MasterWork/PN_Diode/1.csv")
  
