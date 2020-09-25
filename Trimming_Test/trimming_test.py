import numpy as np
import logging
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
from scipy import interpolate
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
#plt.style.use('ggplot')
directory = "Trimming_Test/"
PdfPages = PdfPages('../output_data/trimming_test' + '.pdf')

def plot_BandGap_hex(directory = directory , chip_Id = ["chip_Id"]):
    col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, len(chip_Id)))
    print("===============================Plotting Band Gap test==========================================================")
    for chip in chip_Id:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cmap = plt.cm.get_cmap('tab20', 16)
        BG_hex = []
        Freq_int = []
        BG_mv=[]
        Freq = []
        file = chip+"_BandGap.csv" 
        with open(chip+"/"+file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            print("plotting Band Gap for %s"%chip)
            for row in reader:
               BG_hex = np.append(BG_hex, row[0])
               BG_mv = np.append(BG_mv, float(row[1]))
               #Freq_Hz = np.append(Freq, float(row[1]))
               #BG_mv = np.append(BG_mv, row[2])
        ax.errorbar(BG_hex,BG_mv,0.0,fmt='-', markersize=3, label = chip, color=col_row[chip_Id.index(chip)])
        ax.plot(BG_hex,BG_mv, "o", markerfacecolor='black')
#         ax.set_yticks(range(0, len(BG_array)))
#         ax.set_yticklabels(BG_array)
        ax.grid(True)
        plt.xticks(rotation=90)
        ax.legend() 
        ax.set_xlabel("BandGap voltage [hex]")
        ax.set_ylabel("BandGap voltage [mV]")
        ax.set_title("BandGap voltage for %s "%(chip), fontsize=12)
        plt.savefig(chip+"/"+file+"_hex.png", bbox_inches='tight')
        PdfPages.savefig()
        plt.close(fig)

def plot_Freq_hex(directory = directory , chip_Id = ["chip_Id"]):
    col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, len(chip_Id)))
    print("===============================Plotting Frequency test==========================================================")
    for chip in chip_Id:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cmap = plt.cm.get_cmap('tab20', 16)
        Freq_hex = []
        Freq_int = []
        BG_mv=[]
        Freq = []
        file = chip+"_Freq.csv" 
        with open(chip+"/"+file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            print("plotting Frequency for %s"%chip)
            for row in reader:
               Freq_hex = np.append(Freq_hex, row[0])
               Freq_int = np.append(Freq_int, int(row[0],16))
               Freq = np.append(Freq, float(row[1]))
               BG_mv = np.append(BG_mv, row[2])
        ax.errorbar(Freq_hex,Freq,0.0,fmt='-', markersize=3, label = chip, color=col_row[chip_Id.index(chip)])
        ax.plot(Freq_hex,Freq,"o",markerfacecolor='black')
        #sc = ax.scatter(Freq_hex, Freq, c=BG_int, cmap=cmap, s=50) 
        #cbar = fig.colorbar(sc, ax=ax, orientation='horizontal')
        #cbar.set_ticks(np.linspace(0.5, len(Freq_int), len(Freq_int)+2))
        #cbar.set_ticklabels(BG_hex)
        #cbar.ax.invert_xaxis()
        #cbar.set_label("BandGap Trimming bits [hex]", labelpad=1, fontsize=10)
    
        ax.grid(True)
        plt.xticks(rotation=90)
        ax.legend() 
        ax.set_xlabel("Oscillator Frequency [hex]")
        ax.set_ylabel("Oscillator Frequency [MHz]")
        ax.set_title("Oscillator Frequency for %s at a bandgap voltage %s mV"%(chip, BG_mv[0]), fontsize=12)
        plt.savefig(chip+"/"+file+"_hex.png", bbox_inches='tight')
        PdfPages.savefig()
        plt.close(fig)

def plot_BandGap(directory = directory , chip_Id = ["chip_Id"],txt = ["txt"]):
    col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, len(chip_Id)))
    print("===============================Plotting BandGap test==========================================================")
    for chip in chip_Id:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cmap = plt.cm.get_cmap('tab20', 16)
        BG_hex = []
        BG_int = []
        BG_mv=[]
        Freq = []
        error = []
        freq_optimal = []
        file = chip+"_BandGap.csv" 
        with open(chip+"/"+file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            print("plotting BandGap for %s"%chip)
            for row in reader:
               BG_hex = np.append(BG_hex, row[0])
               BG_int = np.append(BG_int, int(row[0],16))
               BG_mv = np.append(BG_mv, float(row[1]))
               Freq = np.append(Freq, float(row[2]))
               error = np.append(error, float(row[3]))
               freq_optimal = np.append(freq_optimal, row[4])
        #ax.errorbar(BG_mv,Freq,error,fmt='-', markersize=3, label = chip, color=col_row[chip_Id.index(chip)])
        sc = ax.scatter(BG_mv, Freq, c=BG_int, cmap=cmap, s=50) 
        cbar = fig.colorbar(sc, ax=ax, orientation='horizontal')
        cbar.set_ticks(np.linspace(0.5, len(BG_int), len(BG_int)+2))
        cbar.set_ticklabels(BG_hex)
        #cbar.ax.invert_xaxis()
        cbar.set_label("BandGap Trimming bits [hex]", labelpad=1, fontsize=10)

        ax.grid(True)
        #ax.legend() 
        ax.set_xlabel("BandGap voltage [mv]")
        ax.set_ylabel("Oscillator Frequency [MHz]")
        ax.set_title("BandGap Voltage Vs Osc. Freq. [ %s at %s MHz]"%(chip, freq_optimal[0]), fontsize=12)
        
#         ax2 = ax.twiny()
#         ax2.spines['bottom'].set_position(('outward', 50))
#         ax2.set_xlabel("BandGap Trimming bits [hex]")
#         ax2.xaxis.set_ticks_position('bottom')
#         ax2.set_xticks(range(1, len(BG_int)))
#         ax2.set_xticklabels(BG_hex)
#         ax2.xaxis.set_label_coords(0.5, -0.3)
        #ax2.set_xlim((ax.get_xlim()[0], ax.get_xlim()[-1]))
        plt.savefig(chip+"/"+file+".png", bbox_inches='tight')
        PdfPages.savefig()
        plt.close(fig)

def plot_BandGap_All(directory = directory , chip_Id = ["chip_Id"]):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    col_row = plt.cm.BuPu(np.linspace(0.3, 1.9, len(chip_Id)))
    cmap = plt.cm.get_cmap('tab20', 16)
    print("===============================Plotting BandGap test For all the chips==========================================================")
    for chip in chip_Id:
        BG_hex = []
        BG_int = []
        BG_mv=[]
        Freq = []
        error = []
        file = chip+"_BandGap.csv" 
        with open(chip+"/"+file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            print("plotting %s"%chip)
            for row in reader:
               BG_hex = np.append(BG_hex, row[0])
               BG_int = np.append(BG_int, int(row[0],16))
               BG_mv = np.append(BG_mv, float(row[1]))
               Freq = np.append(Freq, float(row[2]))
               error = np.append(error, float(row[3]))
            if chip == "Chip6":
                ax.errorbar(BG_mv[1:],Freq[1:],error[1:],fmt='-', label = chip)#, color=col_row[chip_Id.index(chip)])
                sc = ax.scatter(BG_mv[1:], Freq[1:], c=BG_int[1:], cmap=cmap, s=50) 
                spline = interpolate.splrep(BG_mv[1:],Freq[1:], s=10, k=2)  # create spline interpolation
                xnew = np.linspace(np.min(BG_mv[1:]), np.max(BG_mv[1:]), num = 50, endpoint = True)
                spline_eval = interpolate.splev(xnew, spline)  # evaluate spline
                plt.plot(xnew,spline_eval,"-", label = chip)
            else: 
                #ax.errorbar(BG_mv,Freq,error,fmt='-', label = chip)
                sc = ax.scatter(BG_mv, Freq, c=BG_int, cmap=cmap, s=50)
                spline = interpolate.splrep(BG_mv,Freq, s=10, k=2)  # create spline interpolation
                xnew = np.linspace(np.min(BG_mv), np.max(BG_mv), num = 50, endpoint = True)
                spline_eval = interpolate.splev(xnew, spline)  # evaluate spline
                plt.plot(xnew,spline_eval,"-", label = chip)
             
    cbar = fig.colorbar(sc, ax=ax, orientation='horizontal')
    cbar.set_ticks(np.linspace(0.5, len(BG_int), len(BG_int)+2))
    cbar.set_ticklabels(BG_hex)
    #cbar.ax.invert_xaxis()
    cbar.set_label("BandGap Trimming bits [hex]", labelpad=1, fontsize=10)   
    ax.tick_params(axis='x', labelrotation=90)   
    ax.grid(True)
    ax.legend(prop={'size': 6}) 
    ax.set_xlabel("BandGap voltage [mv]")
    ax.set_ylabel("Oscillator Frequency [MHz]")
    ax.set_title("BandGap configuration Vs Oscillator Frequency", fontsize=12)
    plt.tight_layout()
    plt.savefig("BandGap_Oscillation_All.png", bbox_inches='tight')
    ax.set_xlim([590, 610])
    ax.set_ylim([9.8, 10.15])
    plt.tight_layout()
    plt.savefig("BandGap_Oscillation_All_Zoom.png", bbox_inches='tight')
    PdfPages.savefig()
    plt.close(fig)
    objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')


def plot_config_pattern(directory = directory , chip_Id = ["chip_Id"], file = "Optimal_Values.csv"):
        Freq_array = [hex(x)[2:].upper() for x in np.arange(0, 32,1)] 
        BG_array = [hex(x)[2:].upper() for x in np.arange(0, 16,1)] 
        print("===============================Frequency/BandGap configuration Pattern==========================================")
        fig = plt.figure()
        ax = fig.add_subplot(111)
        chip_id = []
        BG_hex = []
        BG_mv=[]
        Freq_hex = []
        Freq_Mhz = []
        with open(file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            for row in reader:
               chip_id = np.append(chip_id, row[0])
               BG_hex = np.append(BG_hex, row[1])
               BG_mv = np.append(BG_mv, float(row[2]))
               Freq_hex = np.append(Freq_hex, row[3])
               Freq_Mhz = np.append(Freq_Mhz, float(row[4]))
        data_matrix= np.zeros(shape=(len(BG_array),len(Freq_array)), dtype=float)
        for (f, b, c) in zip(Freq_hex, BG_hex, chip_id):
            data_matrix[BG_array.index(b), Freq_array.index(f)] = data_matrix[BG_array.index(b), Freq_array.index(f)]+ 1 #random.randint(0,100)
            ax.text(BG_array.index(b),Freq_array.index(f),c,ha='center',va='center')
        fig, ax = plt.subplots()
        data_masked = np.ma.masked_where(data_matrix == 0, data_matrix)
        cmap = plt.cm.get_cmap('Paired')
        #cmap = plt.get_cmap('tab10')
        im = ax.imshow(data_masked, aspect='auto', origin='lower', cmap=cmap)#, interpolation='gaussian'
        #Set the chip name
        for (f, b, c) in zip(Freq_hex, BG_hex, chip_id):
            ax.text(Freq_array.index(f),BG_array.index(b) ,"["+c+"]",ha='center',va='center')
    
        ax = plt.gca();
        cb = fig.colorbar(im, ax=ax, fraction=0.0594)
        cb.set_label("Chip distribution")
        # Move left and bottom spines outward by 10 points
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['bottom'].set_position(('outward', 10))
        # Hide the right and top spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # Only show ticks on the left and bottom spines
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        ax.set_xlabel('Oscillator trimming bits [hex]')
        ax.set_ylabel('BandGap Trimming bits[hex]')
        ax.set_xticks(range(0, len(Freq_array)))
        ax.set_xticklabels(Freq_array)
        ax.set_yticks(range(0, len(BG_array)))
        ax.set_yticklabels(BG_array)
        plt.xticks(rotation=90)
        ax.set_title('Frequency/BandGap configuration Pattern', fontsize=12)
        ax.grid()
        ax2 = ax.twinx()
        ax2.axis('off')
        #ax2.set_ylim([0, size_I])
        #plt.axhline(y=0, linewidth=2, color='#d62728', linestyle='solid')
        plt.axvline(x=15, linewidth=2, color='#d62728', linestyle='solid')
        
        plt.tight_layout()
        plt.savefig('Configuration pattern.png')
        PdfPages.savefig()
        plt.close(fig)



def plot_BandGap_Bar(file = "Optimal_Values.csv"):
        print("=======================================Plotting Optimal Values==================================================")
        Freq_array = [hex(x)[2:].upper() for x in np.arange(0, 32,1)] 
        BG_array = [hex(x)[2:].upper() for x in np.arange(0, 16,1)]
        col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, len(chip_Id)))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        chip_id = []
        BG_hex = []
        BG_mv=[]
        Freq_hex = []
        Freq_Mhz = []
        with open(file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            for row in reader:
               chip_id = np.append(chip_id, row[0])
               BG_hex = np.append(BG_hex, row[1])
               BG_mv = np.append(BG_mv, float(row[2]))
               Freq_hex = np.append(Freq_hex, row[3])
               Freq_Mhz = np.append(Freq_Mhz, float(row[4]))
        ax.grid()
        ax.bar(np.arange(0, len(chip_id)), [int(x,16) for x in BG_hex],color = col_row[0],  width = 0.3)
        ax.bar(np.arange(-0.25, len(chip_id)-0.25), [int(x,16) for x in Freq_hex] , color = col_row[4], width = 0.3)
        ax.set_xticks(range(0, len(chip_id)))
        ax.set_xticklabels(["Chip"+x for x in chip_id])
        
        ax.set_yticks(range(0, len(BG_array)))
        ax.set_yticklabels(BG_array)
        
        ax.set_ylabel('BandGap Trimming bits[hex]')
        plt.xlabel('Chip Id')
        plt.xticks(rotation=45)
        ax.legend(labels=["BandGap Trimming", "Oscillator Trimming"])
        plt.title('BandGap Trimming bits for different chips[600 mV, 10 MHz]')
        plt.savefig('BandGap_Trimming_bits.png')
        PdfPages.savefig()
        plt.close(fig)
        
        
chip_Id = ["Chip1","Chip1_New" ,"Chip2","Chip3","Chip3_New","Chip4","Chip5","Chip5_New", "Chip6_New","Chip6","Chip7","Chip9"] 
plot_BandGap_Bar()
plot_config_pattern()
plot_Freq_hex(chip_Id = chip_Id)
plot_BandGap_hex(chip_Id = chip_Id)
plot_BandGap(chip_Id = chip_Id)
plot_BandGap_All(chip_Id = chip_Id)
PdfPages.close()