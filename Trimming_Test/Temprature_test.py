import numpy as np
import logging
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
from scipy import interpolate
import matplotlib.ticker as ticker
#%matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)
import pandas as pd
import csv
import matplotlib
from celluloid import Camera
import matplotlib.image as image
import math
import random
import matplotlib.patches as mpatches
from matplotlib.offsetbox import (DrawingArea, OffsetImage,AnnotationBbox)
#plt.style.use('ggplot')
directory = "Trimming_Test/"
PdfPages = PdfPages('../output_data/temp_studies' + '.pdf')

def plot_temp_bandGap(file ="temp_studies.csv", title='Optimal BandGap trim w.r.t  Temperature'):
    x_bins= []
    BG_value = []
    config_value = []
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    with open(file, 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        next(reader)
        for row in reader:
           x_bins = np.append(x_bins, row[0])
           BG_value = np.append(BG_value, row[7])
           config_value = np.append(config_value, row[6])
        BG_value= [float(x) for x in BG_value]
        config_value= [int(x, 2) for x in config_value]
        #config_value_hex = [str(hex(int(x, 2))[2:]) for x in config_value]
    BG = ax1.errorbar(x_bins, BG_value, yerr=0.0, fmt='o-',color='b', label='BG_value')
    ax1.yaxis.label.set_color('b')
    ax1.tick_params(axis='y', colors='b')
    ax1.set_xlabel('Temperature')
    ax1.set_ylabel('BG Voltage [mv]')
    ax1.set_title(title, color="black")
    def to_hex(x, pos):
        return '%X' % int(x)
    
    fmt = ticker.FuncFormatter(to_hex)
    ax2 = ax1.twinx()
    conf = ax2.errorbar(x_bins, config_value, yerr=0.0, fmt='o-', color='g', label='config_value')
    ax2.get_yaxis().set_major_locator(ticker.MultipleLocator(1))
    ax2.get_yaxis().set_major_formatter(fmt)
    ax2.spines['right'].set_position(('outward', 1))
    #ax2.yaxis.set_label_coords(1.15, 1.05)
    ax2.yaxis.label.set_color('g')
    ax2.tick_params(axis='y', colors='g')
    ax2.spines['right'].set_position(('outward', 3))  # adjust the position of the second axis 
    ax2.set_ylabel('configuration [hex]', rotation=90)
    ax2.spines['right'].set_color('g')
    ax1.grid()
    ax2.grid()
    plt.tight_layout()
    PdfPages.savefig()
    plt.savefig("Temperature_BG.png", bbox_inches='tight')
    plt.close(fig)


def plot_temp_oscillator(file ="temp_studies.csv", title='Optimal Oscillator trim w.r.t  Temperature'):
    x_bins= []
    osc_value = []
    osc_config_value = []
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    with open(file, 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        next(reader)
        for row in reader:
           x_bins = np.append(x_bins, row[0])
           osc_value = np.append(osc_value, row[9])
           osc_config_value = np.append(osc_config_value, row[8])
        osc_value= [float(x) for x in osc_value]
        osc_config_value= [int(x, 2) for x in osc_config_value]
        #config_value_hex = [str(hex(int(x, 2))[2:]) for x in config_value]
    BG = ax1.errorbar(x_bins, osc_value, yerr=0.0, fmt='o-',color='b', label='Oscillator value')
    ax1.yaxis.label.set_color('b')
    ax1.tick_params(axis='y', colors='b')
    ax1.set_xlabel('Temperature')
    ax1.set_ylabel('Oscillator value [MHz]')
    ax1.set_title(title, color="black")
    def to_hex(x, pos):
        return '%X' % int(x)
    
    fmt = ticker.FuncFormatter(to_hex)
    ax2 = ax1.twinx()
    conf = ax2.errorbar(x_bins, osc_config_value, yerr=0.0, fmt='o-', color='g', label='Oscillator trimming value')
    ax2.get_yaxis().set_major_locator(ticker.MultipleLocator(1))
    ax2.get_yaxis().set_major_formatter(fmt)
    ax2.spines['right'].set_position(('outward', 1))
    #ax2.yaxis.set_label_coords(1.15, 1.05)
    ax2.yaxis.label.set_color('g')
    ax2.tick_params(axis='y', colors='g')
    ax2.spines['right'].set_position(('outward', 3))  # adjust the position of the second axis 
    ax2.set_ylabel('Configuration [hex]', rotation=90)
    ax2.spines['right'].set_color('g')
    ax1.grid()
    ax2.grid()
    plt.tight_layout()
    PdfPages.savefig()
    plt.savefig("Temperature_oscillator.png", bbox_inches='tight')
    plt.close(fig)

plot_temp_bandGap()
plot_temp_oscillator()
PdfPages.close()