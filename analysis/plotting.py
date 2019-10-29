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
from matplotlib.pyplot import *
import matplotlib.pyplot as plt
from analysis import analysis
from analysis import logger
colors = ['black', 'red', '#006381',"blue",  '#33D1FF', '#F5A9BC', 'grey', '#7e0044', 'orange', "maroon", 'green', "magenta", '#33D1FF','#7e0044',  "yellow"]

class Plotting(object):     
    def __init__(self):
        self.log = logger.setup_derived_logger('Plotting')
        self.log.info('Plotting initialized')
        
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

# A special class to plot the attenuation coefficient for several materials
class Attenuation(object):
     
    def __init__(self):
        print("Plotting Attenuation class initialized")
    
    def mass_attenuation_coeff(self, Directory=False, PdfPages=False, targets=False):
        for target in targets:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            data = loadtxt(Directory + target +
                           "/mass_attenuation_coeff_in_detail_"+target+".dat")
            x = data[:, 0]  # Energy in Kev
            # total mass attenuation coeff with coherent scattering
            y = data[:, 6]
            # mass attenuation coeff due to photoelectric effect
            p = data[:, 3]
            # mass attenuation coeff due to compton (incoherent) scattering
            i = data[:, 2]
            # mass attenuation coeff due to rayleigh (coherent) scattering
            r = data[:, 1]
            # mass attenuation coeff due to pair production in nuclei field
            ppn = data[:, 4]
            # mass attenuation coeff due to pair production in electron field
            ppe = data[:, 5]
            plt.plot(x*10**3, ppe, ':', color='orange',
                     label='Pair production (electron)')
            plt.plot(x*10**3, ppn, ':', color='grey',
                     label='Pair production (nuclei)')
            #plt.plot(x*10**3, r, '--', color='green', label='Coherent scattering')
            plt.plot(x*10**3, i, '--', color='#006381',
                     label='Compton scattering')
            plt.plot(x*10**3, p, '-.', color='#7e0044',
                     label='Photoelectric effect')
            plt.plot(x*10**3, y, '-', color='black', label='Total')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Photon energy [keV]')
            ax.grid(True)
            ax.set_ylabel('Mass attenuation coefficient [cm$^2$/g]')
            ax.set_title(r'Mass attenuation coefficient for %s ' %
                         target, fontsize=11)
            ax.legend(loc="upper right")
            plt.xlim(1, 1000000)
            plt.tight_layout()
            plt.savefig(Directory+target+"/mass_attenuation_coeff_" +
                        target+".png", bbox_inches='tight')
            PdfPages.savefig()

    def attenuation_thickness(self, Directory=False, PdfPages=False, targets=False, logx=True, logy=True, color=colors):

        for target in targets:
            Density = []
            Mu = []
            Energy = []
            x = np.arange(0, 20, 0.001)
            y = []
            with open(Directory + target+"/Attenuation_Energy_"+target+".csv", 'r')as parameters:
                fig = plt.figure()
                ax = fig.add_subplot(111)
                reader = csv.reader(parameters)
                next(reader)
                for row in reader:
                    Density = np.append(Density, float(row[0]))
                    Mu = np.append(Mu, float(row[1]))
                    Energy = np.append(Energy, float(row[2]))
                for i in np.arange(len(Energy)):
                    y = np.exp((-1) * Mu[i] * Density[0] * x)
                    ax.plot(x, y, ':', label=str(Energy[i])+'Kev')
                    if ((Energy[i] == 60.0) and (target != "Be")):
                        l = np.log(10**(-9))/((-1)*Mu[i] * Density[0])
                        print ("to get 10e-9 of the initial intensity in %s  %5.3f cm shielding is needed"%(target,l))
                        ax.annotate("%5.3f cm" % l, xy=(l, 10**(-9)), xytext=(l+1, 10**(-8)),
                                    arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=-0.5", relpos=(.6, 0.), fc="w"))
                        # Define the shielding thickness
                        ax.axvline(x=l, linewidth=2,
                                   color='#d62728', linestyle='solid')
                    # ax.axhline(y=10**(-9), linewidth=2, color='#d62728', linestyle='solid')# Define the shielding thickness
                    ax.set_ylim(bottom=10**(-10))
                    ax.set_xlim(0.001, 150)
                    # ax.set_yscale('log')
            if target == "Be":
                ax.axvline(x=0.03, linewidth=2,
                           color='#d62728', linestyle='solid')
                ax.annotate("%5.3f cm" % 0.03, xy=(0.03, 0), xytext=(0.03+0.1, 0.2),
                            arrowprops=dict(arrowstyle="-|>",
                                            connectionstyle="arc3,rad=-0.5", relpos=(.2, 0.), fc="w"))
                ax.set_xlim(0.001, 10)
            if logx:
                ax.set_xscale('log')

            ax.grid(True)
            ax.set_xlabel(target+' Thickness (cm)')
            ax.set_ylabel('Transmission $I$/$I_0$ ')
            ax.legend(loc='upper right')
            ax.set_title(r'Transmission of x rays through %s Filter' %
                         target, fontsize=11)
            plt.tight_layout()
            plt.savefig(Directory+target+"/Thickness_" +
                        target+".png", bbox_inches='tight')
            PdfPages.savefig()

    def attenuation_Energy(self, Directory=False, PdfPages=False, targets=False, logx=True, logy=True, n=False, x_offset=False, y_offset=False, color=colors):

        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in np.arange(len(targets)):
            data = loadtxt(
                Directory + targets[i]+"/mass_attenuation_coeff_in_detail_"+targets[i]+".dat")
            x = data[:, 0]  # Energy in Kev
            # total mass attenuation coeff with coherent scattering
            y = data[:, 6]

            ax.plot(x*10**3, y, '-', color=color[i], label=targets[i])
        ax = plt.gca()  # .invert_xaxis()
        for j, txt in enumerate(n):
            ax.annotate(
                txt, xy=(x_offset[j], y_offset[j]), color=color[j], size=6)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Photon energy [keV]')
        ax.grid(True)
        ax.set_ylabel('Mass attenuation coefficient [cm$^2$/g]')
        #ax.set_title(r"Mass attenuation coefficients as a function of Energy", fontsize=10)
        plt.ylim(1, 10000)
        plt.xlim(1, 60)
        ax.legend()
        plt.tight_layout()
        plt.savefig(Directory+"/attenuation_Energy_relation.png",
                    bbox_inches='tight')
        PdfPages.savefig()

        
    def close(self,PdfPages=False):
            PdfPages.close()


        