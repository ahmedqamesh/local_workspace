from __future__ import division
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from kafe import *
from kafe.function_library import quadratic_3par
from numpy import loadtxt, arange
import matplotlib.ticker as mtick
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.backends.backend_pdf import PdfPages
import csv
from scipy.optimize import curve_fit
import tables as tb
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as ticker
import itertools
from matplotlib.colors import LogNorm
from matplotlib import pyplot as p
from mpl_toolkits.mplot3d import Axes3D    # @UnusedImport
from math import pi, cos, sin
import logging
from scipy.linalg import norm
import os
import matplotlib as mpl
from matplotlib import gridspec
import seaborn as sns
sns.set(style="white", color_codes=True)
from matplotlib.patches import Circle
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import matplotlib.transforms as mtransforms
from matplotlib.ticker import NullFormatter
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
import pylab as P
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
from matplotlib.pyplot import *
import matplotlib.pyplot as plt
from analysis import analysis

class Plotting(object):
     
    def __init__(self):
        print("Plotting initialized")
    
    colors = ['black', 'red', '#006381',"blue",  '#33D1FF', '#F5A9BC', 'grey', '#7e0044', 'orange', "maroon", 'green', "magenta", '#33D1FF','#7e0044',  "yellow"]
    def plot_linear(self, Directory=False, colors=colors, PdfPages=False,text =False,txt ="Text",
                     x=np.arange(1,10),x_label="Supply current I_s [A]",y=np.arange(1,10),y_label="Needed Voltage U_S [V]",
                     map= False,z=np.arange(1,10),z_label="Transferred Efficiency",test= "DCConverter",title="powerSupply_Voltage", p=[1,2,3],
                     line =None,data_line = [0],data_label ='Power loss in the cable $P_c$ [W]'):
        '''
        PLot a relation between two variables 
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111)
        if map:
            cmap = plt.cm.get_cmap('viridis', 15)
            sc= ax.scatter(x, y,c=z,cmap=cmap, s=8)
            cbar = fig.colorbar(sc, ax=ax, orientation='horizontal')
            cbar.ax.invert_xaxis()
            cbar.set_label(z_label,labelpad=1,fontsize=10)
            plt.axvline(x=4, linewidth=0.8, color=colors[1], linestyle='dashed')
            plt.axhline(y=22.5, linewidth=0.8, color=colors[1], linestyle='dashed')
        else:
            sc= ax.errorbar(x, y, xerr=0.0, yerr=0.0, fmt='o', color=colors[1], markersize=3, ecolor='black')
            ax.plot(x,y, linestyle="-",color=colors[0], label="Fit",markersize=1)       
            #ax.legend(loc="upper right")
            #ax.set_ylim(ymin=min(y)-10)
        ax.set_xlabel(x_label,fontsize=10)
        ax.set_title(title, fontsize=8)
        ax.set_ylabel(y_label,fontsize=10)
        ax.ticklabel_format(useOffset=False)
        ax.grid(True)
        if text:
            ax.text(0.95, 0.45, txt, fontsize=8,
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))
                            
        if line:
            # Create axes for loss and voltage 
            ax2 = ax.twinx()
            line = ax2.errorbar(x, data_line, xerr=0.0, yerr=0.0, fmt='o', color=colors[3], markersize=1, ecolor='black')  # plot power loss
            ax2.yaxis.label.set_color(colors[3])
            ax2.tick_params(axis='y', colors=colors[3])
            ax2.spines['right'].set_position(('outward',3)) # adjust the position of the second axis 
            ax2.set_ylabel(data_label, rotation=90, fontsize=10)
            
        fig.savefig(Directory + "/output/"+test+".png", bbox_inches='tight')
        plt.tight_layout()
        PdfPages.savefig()
        
    def close(self,PdfPages=False):
            PdfPages.close()
        