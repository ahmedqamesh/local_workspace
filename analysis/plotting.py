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
colors = ['black', 'red', '#006381', "blue", '#33D1FF', '#F5A9BC', 'grey', '#7e0044', 'orange', "maroon", 'green', "magenta", '#33D1FF', '#7e0044', "yellow"]
#colors = plt.cm.BuPu(np.linspace(0.3, 0.9, 20))
an = analysis.Analysis()
class Plotting(object):     

    def __init__(self):
        self.log = logger.setup_derived_logger('Plotting')
        self.log.info('Plotting initialized')
        
    def plot_linear(self, directory=False, colors=colors, PdfPages=False, text=False, txt="Text",
                     x=np.arange(1, 10), x_label="Supply current I_s [A]", y=np.arange(1, 10), y_label="Needed Voltage U_S [V]",show=False,
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
            #plt.axvline(x=0.8*1000, linewidth=0.8, color=colors[1], linestyle='dashed')
            #plt.axhline(y=24, linewidth=0.8, color=colors[1], linestyle='dashed')
        else:
            sc = ax.errorbar(x, y, xerr=0.0, yerr=0.0, fmt='o', color=colors[1], markersize=3, ecolor='black')
            #ax.plot(x, y, linestyle="-", color=colors[0], label="Fit: ", markersize=1)
            sig = [0.4 * y[k] for k in range(len(y))]
            popt, pcov = curve_fit(an.linear, x, y, sigma=sig, absolute_sigma=True, maxfev=5000, p0=(0.47, 0))
            xline = np.linspace(x[0], x[-1], 100) 
            a, b = popt[0], popt[1]
            a_err, b_err = np.absolute(pcov[0][0]) ** 0.5, np.absolute(pcov[1][1]) ** 0.5
            line_fit_legend_entry='Fit parameters:\n a=%.2f$\pm$ %.2f\n b=%.2f$\pm$ %.2f\n' % (a, a_err, b, b_err)
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


    def plot_lines(self,x1 = None, y1 =None, z1= None,directory=None,PdfPages=PdfPages):
        '''
        PLot a relation between two variables 
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cmap = plt.cm.get_cmap('viridis', 15)
       # x =[x1[i]/x1[i]*2 for i in range(len(x1))]
        #ax.fill_between(x1-1, x,1.4,facecolor='yellow', alpha=0.5)
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
