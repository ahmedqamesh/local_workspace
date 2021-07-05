from __future__ import division
import numpy as np
from kafe import *
from kafe.function_library import quadratic_3par
from numpy import loadtxt, arange
import csv
from scipy.optimize import curve_fit
import tables as tb
from mpl_toolkits.mplot3d import Axes3D
import itertools
from mpl_toolkits.mplot3d import Axes3D  # @UnusedImport
from math import pi, cos, sin
from scipy.linalg import norm
import os
import seaborn as sns
sns.set(style="white", color_codes=True)

from matplotlib.pyplot import *
import pylab as P
import matplotlib as mpl
import matplotlib.ticker as ticker
import matplotlib.transforms as mtransforms
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import gridspec
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import NullFormatter
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from analysis import analysis
from analysis import logger
import matplotlib.image as image
from scipy import interpolate
colors = ['black', 'red', '#006381', "blue", '#33D1FF', '#F5A9BC', 'grey', '#7e0044', 'orange', "maroon", 'green', "magenta", '#33D1FF', '#7e0044', "yellow"]
#an = analysis.Analysis()

class Plotting(object): 

    def __init__(self):
        self.log = logger.setup_derived_logger('Plotting')
        self.log.info('Plotting initialized')
    
    def plot_voltage_dcconverter(self, dir=None , file=None, output="output", PdfPages=None, directory=None, ylim=4000, title="title", logo=True):
        im = image.imread(directory + dir + 'icon.png')
        
        col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, 5))
        v_sin = []
        v_cin = []
        v_cout = []
        I_sin = []
        I_sin_err = []
        I_cout = []
        I_cout_err = []    
        f = 1000  # to convert to mA
        with open(directory + dir + file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            for row in reader:
                v_sin = np.append(v_sin, float(row[0]))
                v_cin = np.append(v_cin, float(row[1]))
                v_cout = np.append(v_cout, float(row[2]))
                
                I_sin = np.append(I_sin, float(row[3]) * f)
                I_sin_err = np.append(I_sin_err, float(row[4]) * f)
                
                I_cout = np.append(I_cout, float(row[5]) * f)
                I_cout_err = np.append(I_cout_err, float(row[6]) * f)
        fig = plt.figure()
        gs = gridspec.GridSpec(2, 1, height_ratios=[2, 2])
        ax = plt.subplot(gs[0])
        ax1 = plt.subplot(gs[1])        
        cmap = plt.cm.get_cmap('viridis', 15)
       # ax.errorbar(v_sin, v_cin, yerr=0.0, color=col_row[0], fmt='-p', markerfacecolor='white', markeredgecolor=col_row[0], ms=4, label="Input Voltage to the DC/DC module")
        ax.errorbar(v_sin, v_cout, yerr=0.0, color=col_row[3], fmt='-p' , markerfacecolor='white', markeredgecolor=col_row[3], ms=4, label="Output Voltage from the DC/DC module")
        # ax.plot(v_sin, v_cin , color=col_row[0], label="Input Voltage to the module")
        ax.plot(v_sin, v_cout, color=col_row[3])
        ax.text(0.95, 0.35, dir[:-1], fontsize=8,
                horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))    
        ax.ticklabel_format(useOffset=False)
        ax.grid(True)
        ax.legend(loc="upper left", prop={'size': 8})
        ax.set_ylabel("Voltage [V]")
        ax.set_ylim([-0.5, 5])
        ax.autoscale(enable=True, axis='x', tight=None)
        ax.set_title(title, fontsize=10)
        
        ax1.errorbar(v_sin, I_sin, yerr=I_sin_err, color=col_row[0], fmt='-p', markerfacecolor='white', ms=4, label="Input Current")
        ax1.errorbar(v_sin, I_cout, yerr=I_cout_err, color=col_row[3], fmt='-p' , ms=4, markerfacecolor='white', label="Load Current by the module")
        
        ax1.plot(v_sin, I_sin , color=col_row[0])
        ax1.plot(v_sin, I_cout, color=col_row[3])
        ax1.grid(True)
        ax1.set_xlabel("Power Supply Voltage $U_S$ [V]")
        ax1.set_ylabel(r'Current I [mA]')
        ax1.set_ylim([-10, ylim])
        ax1.legend(loc="upper left", prop={'size': 8})
        fig.figimage(im, 5, 5, zorder=1, alpha=0.08, resize=False)
        plt.tight_layout()
        plt.savefig(directory + dir + output, bbox_inches='tight')
        PdfPages.savefig()
        
    def plot_efficiency_dcconverter(self, dir=None , txt="txt", a=8 , file=None, output="output", PdfPages=None, directory=None, xlim=[5, 40], title="title", logo=True):
        im = image.imread(directory + dir + 'icon.png')
        col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, 5))
        v_sin = []
        V_cin = []
        v_cout = []
        I_sin = []
        I_sin_err = []
        I_cout = []
        I_cout_err = []    
        f = 1000  # to convert to mA
        efficiency = []
        with open(directory + dir + file, 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            for row in reader:
                v_sin = np.append(v_sin, float(row[0]))
                V_cin = np.append(V_cin, float(row[1]))
                
                v_cout = np.append(v_cout, float(row[2]))
                
                I_sin = np.append(I_sin, float(row[3]) * f)
                I_sin_err = np.append(I_sin_err, float(row[4]) * f)
                
                I_cout = np.append(I_cout, float(row[5]) * f)
                I_cout_err = np.append(I_cout_err, float(row[6]) * f)
                if float(row[2]) != 0:
                    efficiency = np.append(efficiency, float(row[2]) * float(row[5]) * 100 / (float(row[0]) * float(row[3])))
                else: 
                    efficiency = np.append(efficiency, 0)
    
        fig = plt.figure()
        ax = fig.add_subplot(111)   
        spline = interpolate.splrep(v_sin[a:], efficiency[a:], s=10, k=2)  # create spline interpolation
        xnew = np.linspace(np.min(v_sin[a:]), np.max(v_sin[a:]), num=50, endpoint=True)
        spline_eval = interpolate.splev(xnew, spline)  # evaluate spline
        plt.plot(v_sin[a:], efficiency[a:], 'o', xnew, spline_eval, "-")
        ax.ticklabel_format(useOffset=False)
        ax.grid(True)
        ax.text(0.95, 0.35, txt, fontsize=8,
                horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))    
        ax.set_ylabel("efficiency [%]")
        ax.set_xlabel("Power Supply Voltage $U_S$ [V]")
        ax.autoscale(enable=True, axis='x', tight=None)
        ax.set_title(title, fontsize=12)
        ax.set_xlim(xlim)
        ax.set_ylim([0, 100])
        fig.figimage(im, 5, 5, zorder=1, alpha=0.08, resize=False)
        plt.tight_layout()
        plt.savefig(directory + dir + output, bbox_inches='tight')
        PdfPages.savefig()
        
    def plot_linear(self, directory=False, colors=colors, PdfPages=False, text=False, txt="Text",
                     x=np.arange(1, 10), x_label="Supply current I_s [A]", y=np.arange(1, 10), y_label="Needed Voltage U_S [V]", show=False,
                     map=False, z=np.arange(1, 10), z_label="Transferred Efficiency", test="DCConverter", title="powerSupply_Voltage", p=[1, 2, 3],
                     line=None, data_line=[0], data_label='Power loss in the cable $P_c$ [W]'):
        '''
        PLot a relation between two variables 
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111)

        if map:
            cmap = plt.cm.get_cmap('viridis', 15)
            sc = ax.scatter(x, y, c=z, cmap=cmap, s=8)
            cbar = fig.colorbar(sc, ax=ax, orientation='horizontal')
            cbar.ax.invert_xaxis()
            cbar.set_label(z_label, labelpad=1, fontsize=10)
            # plt.axvline(x=0.8*1000, linewidth=0.8, color=colors[1], linestyle='dashed')
            # plt.axhline(y=24, linewidth=0.8, color=colors[1], linestyle='dashed')
        else:
            sc = ax.errorbar(x, y, xerr=0.0, yerr=0.0, fmt='o', color=colors[1], markersize=3, ecolor='black')
            # ax.plot(x, y, linestyle="-", color=colors[0], label="Fit: ", markersize=1)
            sig = [0.4 * y[k] for k in range(len(y))]
            popt, pcov = curve_fit(an.linear, x, y, sigma=sig, absolute_sigma=True, maxfev=5000, p0=(0.47, 0))
            xline = np.linspace(x[0], x[-1], 100) 
            a, b = popt[0], popt[1]
            a_err, b_err = np.absolute(pcov[0][0]) ** 0.5, np.absolute(pcov[1][1]) ** 0.5
            line_fit_legend_entry = 'Fit parameters:\n a=%.2f$\pm$ %.2f\n b=%.2f$\pm$ %.2f\n' % (a, a_err, b, b_err)
            ax.plot(xline, an.linear(xline, *popt), '-', lw=1, label=line_fit_legend_entry, markersize=9)  # plot fitted function
            
            ax.legend(loc="upper right")
            # ax.set_ylim(ymin=min(y)-10)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_title(title, fontsize=8)
        ax.set_ylabel(y_label, fontsize=10)
        ax.ticklabel_format(useOffset=False)
        ax.grid(True)
        if text:
            ax.text(0.95, 0.15, txt, fontsize=8,
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))          
        if line:
            # Create axes for loss and voltage 
            ax2 = ax.twinx()
            a = 3
            line = ax2.errorbar(x, data_line, xerr=0.0, yerr=0.0, fmt='o', color=colors[a], markersize=1, ecolor='black')  # plot power loss
            ax2.yaxis.label.set_color(colors[a])
            ax2.tick_params(axis='y', colors=colors[a])
            ax2.spines['right'].set_position(('outward', 3))  # adjust the position of the second axis 
            ax2.set_ylabel(data_label, rotation=90, fontsize=10)
        plt.tight_layout()    
        fig.savefig(directory + "/output/" + test + ".png", bbox_inches='tight')
        PdfPages.savefig()
        
        if show:
            plt.show()

    def plot_lines(self, x1=None, y1=None, z1=None, directory=None, PdfPages=PdfPages):
        '''
        PLot a relation between two variables 
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cmap = plt.cm.get_cmap('viridis', 15)
       # x =[x1[i]/x1[i]*2 for i in range(len(x1))]
        # ax.fill_between(x1-1, x,1.4,facecolor='yellow', alpha=0.5)
        sc = ax.scatter(x1, y1, c=z1, cmap=cmap, s=10)
        cbar = fig.colorbar(sc, ax=ax, orientation='vertical')
        cbar.set_label("Voltage limits [V]", labelpad=1, fontsize=10)
        plt.axvline(x=2.6, linewidth=0.8, color="red", linestyle='dashed')
        ax.set_ylabel("Mops Voltage $U_M$ [v]", fontsize=10)
        ax.set_title("Voltage across one Mops $U_M$ [V] When the other one is disconnected", fontsize=8)
        ax.set_xlabel("Supply Voltage $U_S$ [V]", fontsize=10)
        ax.ticklabel_format(useOffset=False)
        ax.grid(True)
        fig.savefig(directory + "output/MopsVoltageDrop.png", bbox_inches='tight')
        plt.tight_layout()
        PdfPages.savefig()
           
    def close(self, PdfPages=False):
            PdfPages.close()
