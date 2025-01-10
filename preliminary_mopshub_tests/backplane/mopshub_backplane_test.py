import sys
import os
from validators import length
import seaborn as sns
import numpy as np
import logging
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
import matplotlib.pyplot as plt
import pandas as pd
import csv
import matplotlib
from celluloid import Camera
from scipy import interpolate
import math
from matplotlib.backends.backend_pdf import PdfPages
import logging
from reportlab.lib import logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger("CIC")
rootdir = os.path.dirname(os.path.abspath(__file__))
root_dir = rootdir+"/"
from plot_style import *

def plot_backplane_resistance(ylim=4000, text_enable=False):
    
    data_file = root_dir+"data_files/backplane_resistance_results.csv"
    logger.info(f'Reading the file{data_file}')
    data = pd.read_csv(data_file)
    #data.columns = ['', 'Meas','signal','slotpin',"mon_ilk_pin"  ,  "sense_count" ,   "ml_count" ,   "resistance"  ,  "result"] 
    fig1, ax1 = plt.subplots()
    # Print FWHM values for each row
    for index, row in data.iterrows():
        #print(f'Row {index + 1}, I values: {row.iloc[9:].tolist()}')
        #ax1.errorbar(range(0, len(row.iloc[9:])), row.iloc[9:], yerr=0.0, color=col_row[0], fmt='o' , markerfacecolor='black', markeredgecolor='black', ms=marker_size)
        plt.hist(data["mean_resistance"], bins=10, edgecolor='black')
    ax1.ticklabel_format(useOffset=False)
    ax1.grid(True)
    #ax1.legend(loc="upper left", prop={'size': legend_font})
    plt.yscale('log')
    ax1.set_ylabel("Number of averaged measurements")
    ax1.set_xlabel("Resistance in Ohm")
    if text_enable: ax1.set_title("Resistance Measurements for the backplane")
    plt.tight_layout()
    plt.savefig(root_dir+"backplane_resistance_results.pdf", bbox_inches='tight')
    #ax1.set_title("Resistance Measurements for the backplane"     

if __name__ == '__main__':
    plot_backplane_resistance()
    print(root_dir)
    
    