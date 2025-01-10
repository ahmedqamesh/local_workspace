########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.01.2022
"""
########################################################
from __future__ import division
import numpy as np
from numpy import loadtxt, arange
import csv
from scipy.optimize import curve_fit
import tables as tb
from mpl_toolkits.mplot3d import Axes3D
import itertools
from mpl_toolkits.mplot3d import Axes3D  # @UnusedImport
from matplotlib.ticker import FormatStrFormatter
from math import pi, cos, sin
from scipy.linalg import norm
import os
import seaborn as sns
from matplotlib.pyplot import *
import pylab as P
import pandas as pd
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
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from .analysis_utils      import AnalysisUtils
import matplotlib.image as image
from collections import OrderedDict
from scipy import interpolate
from .logger_main   import Logger
from .plot_style import *
import logging
from collections import Counter
import seaborn as sns
from validators import length
log_format = '%(log_color)s[%(levelname)s]  - %(name)s -%(message)s'
log_call = Logger(log_format=log_format, name="Plotting", console_loglevel=logging.INFO, logger_file=False)
logger = log_call.setup_main_logger()#


class Plotting(object): 

    def __init__(self):
        pass
    
    def calculate_dose(self, period):
        """
        Calculate the dose for each period based on the dose rate.
        
        Parameters:
            periods (array-like): Array of time periods.
            dose_rate (float): Dose rate in gray per hour.
        
        Returns:
            array: Array containing the dose for each period.
        """
        dose_rate = 2 #gy/hr
        return [h * dose_rate for h in period]
 
     
    def analyze_magenteic_field(self, file_out=None, PdfPages=None):
        x = np.arange(-5, 5, 1)
        y = np.arange(-7, 7, 1)
        cmap = plt.cm.get_cmap('viridis') 
        # Create a grid of coordinates
        coordinates = [(i, j) for i in x for j in y]
        
        B_field= [230, 260, 230,280,260,290,233,283,266,268,
                   300, 299, 304,319,340,353,350,380,347,381,
                   291, 300, 300,310,320,320,343,340,324,362,
                   283,280,280,293,291,296,322,310,313,345,
                   289,280,280,298,280,284,305,294,306,337,
                   296,280,283,275,269,279,285,284,300,332,
                   295,233,279,271,264,266,276,279,300,327,
                   297,284,274,267,263,262,270,276,300,323,
                   301,284,268,264,260,261,262,277,300,326,
                   301,284,272,256,266,266,270,265,304,328,
                   304,294,285,278,283,284,287,240,318,331,
                   326,305,316,300,310,308,310,380,337,339,
                   337,355,348,343,341,334,351,360,366,359,
                   385,394,368,354,334,374,380,380,389,381]  # magnetic field strength at each point (mT)
        
        # Convert coordinates and B_field to NumPy arrays
        coordinates_arr = np.array(coordinates)
        B_field_arr = np.array(B_field)
        # Reshape B_field to fit the 2D grid
        B_field_grid = B_field_arr.reshape(len(y), len(x))
        
        
        # Plotting using plt.streamplot
        fig, ax = plt.subplots()
        #plt.scatter(x_points, y_points, c=B_field, cmap=cmap, s=100, edgecolors='k', label='Measurement Points')
        plt.imshow(B_field_grid, cmap=cmap, interpolation='nearest', aspect='auto',origin='lower')
        plt.colorbar(label='Magnetic Field Strength (mT)')
        
        plt.title('Magnetic Field Map at Plane A')
        plt.xlabel('X Coordinates [cm]')
        plt.ylabel('Y Coordinates [cm]')
        plt.grid(True)
        fig.savefig(file_out+"_magnetic_field.pdf", bbox_inches='tight')  
        
        if PdfPages:
            PdfPages.savefig()
    
    def plot_histogram(self,xValues =  None, zValues = None, xlabel="Value",modules_name =[0],  ylabel="# Measurements", title="Histogram", bins=10, file_out=None, PdfPages=None):
        
        
        xValues = np.array(xValues)
        # Calculate the differences
        #xValues = np.diff(xValues)
        cmap = plt.cm.get_cmap('viridis')   # Choose a colormap          
                   
        fig2, ax2 = plt.subplots()
        # Plotting
        #fig2, (ax3, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        consecutive_array, repeats, zValues = AnalysisUtils().count_consecutive_repeats(zValues)
        voltage_frequency = dict(Counter(xValues))
        hist_volt = {}
        replaced_volt_dict = {}

        for element, frequency in voltage_frequency.items(): replaced_volt_dict[element] = [zValues[i]*2 for i, x in enumerate(xValues) if x == element]
        # Extract keys (voltages) and values (temperature arrays) from the dictionary
        if modules_name[0] == "during_TID":
            replaced_volt_dict = OrderedDict(sorted(replaced_volt_dict.items()))
            bins , round_factor = bins, 2
        else: 
            for key in replaced_volt_dict:
                replaced_volt_dict[key] = [0] * len(replaced_volt_dict[key])
                replaced_volt_dict = OrderedDict(sorted(replaced_volt_dict.items()))
            bins , round_factor = 5 , 3   
        
        voltages = list(replaced_volt_dict.keys())
        dose_arrays = list(replaced_volt_dict.values())
        # Determine the maximum number of temperature readings for padding
        max_len = max(len(arr) for arr in dose_arrays)
        # Create a matrix to store temperatures with NaN padding
        matrix = np.full((max_len, len(voltages)), np.nan)

        # Fill the matrix with temperature values
        for i, voltage in enumerate(voltages):
            matrix[:len(replaced_volt_dict[voltage]), i] = replaced_volt_dict[voltage]
        start_index = 0
        max_voltage = max(xValues)
        min_voltage = min(xValues)
        ctick_size = (max_voltage - min_voltage) / (bins)  
        plot_range = np.round(np.arange(min_voltage, max_voltage, ctick_size),3)
        tick_size = 1

        # Prepare data for histogram
        x_ticks = np.arange(0, len(voltages),bins)
        # Prepare for Fit        
        voltages_hist, counts_hist = zip(*voltage_frequency.items())
        
        def _gauss(x, *p):
            amplitude, mu, sigma = p
            return amplitude * np.exp(- (x - mu)**2.0 / (2.0 * sigma**2.0))
        
        # Initial guess for the parameters
        initial_guess = [max(counts_hist), np.mean(voltages_hist), np.std(voltages_hist)]
        coeff = None
        # Function to calculate Gaussian (normal) distribution
        
        try:
            coeff, _ = curve_fit(_gauss, voltages_hist, counts_hist, p0=initial_guess)
            # Extract the optimal parameters
            A_opt, mu_opt, sigma_opt = coeff
            # Generate x values for the fitted curve
            x_fit = np.linspace(min(voltages_hist), max(voltages_hist), 100)
            y_fit = _gauss(x_fit, *coeff)
            #ax3.scatter(voltages_hist, counts_hist, label='Data', color='red')
            # Overlay the Gaussian fit
            ax2.plot(np.interp(x_fit, voltages, np.arange(len(voltages))), y_fit, label='Gaussian fit')
            # Set x-axis ticks and labels for the heatmap
            #ax2.legend()
            # Display the fit parameters on the plot
            textstr = ''.join((
                r'$\mu=%.3f\pm %.3f$ V' % (mu_opt,sigma_opt)))
            # these are matplotlib.patch.Patch properties
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            
            # place a text box in upper left in axes coords
            ax2.text(0.65, 0.70, textstr, transform=ax2.transAxes,
                    verticalalignment='top', bbox=props)
        except: 
            pass
        
        cax = ax2.imshow(matrix, cmap=cmap, interpolation='nearest', aspect='auto',origin='lower', vmin=0, vmax=np.nanmax(matrix)+5)
        if modules_name[0] == "during_TID":
            plt.colorbar(cax, ax=ax2, label='Dose [Gy]')
        else:
            pass
        # Set x-axis ticks and labels every 2 steps
        
        x_labels = [str(round(voltages[i],round_factor)) if i % bins == 0 else '' for i in x_ticks]
        ax2.set_xticks(x_ticks)
        ax2.set_xticklabels(x_labels, rotation=0)
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)
        ax2.set_title(title)
        # Apply custom tick lengths to x-axis ticks
        #ax.set_xlim(min(xValues)-0.2, max(xValues)+0.2)  # Set x-axis range from 3 to 6
        # Adding grid lines
        ax2.set_ylim(0, max_len+20)  
        #ax2.set_xlim(4.8, max_len+100)  
        fig2.savefig(file_out[:-4]+"_volt.pdf", bbox_inches='tight')  
        
        if PdfPages:
            PdfPages.savefig()
        
        if PdfPages:
            PdfPages.savefig()
    
        return fig2, ax2

    def plot_data(self, xValues = None, yValues = None, eyValues = [0], xLabel = None, yLabel = None,
                    ymax = None, ymin= None, ymax2 = None, modules_name= ["vorTID"], 
                    yValues2 = None, yLabel2 = None,title = None, posX = None, 
                    posY = None,steps = None,file_out = None,  min_scale = None,  PdfPages = None):
        
        fig, ax = plt.subplots()
        yMin = [0 for i in range(len(yValues))]
        yMax = [0 for i in range(len(yValues))]
        legend_handles = []
        
        #ax = plot.subplot(posX, 1, posY)
        #fig = plot.gcf()
        ax.set_title(title)
        #for number, (value, evalue) in enumerate(zip(yValues, eyValues)):
        for number, value in enumerate(yValues):
            yMin[number] = min((y for y in value if y is not None),key=lambda x:float(x))
            yMax[number] = max((y for y in value if y is not None),key=lambda x:float(x))
            
            #ax.errorbar(xValues, value, xerr=0.0, yerr=evalue, fmt='o', color='black')  # plot points
            axis_1 = ax.plot(xValues,value,'.-', label = yLabel[number+1])            
            colors = [line.get_color() for line in ax.get_lines()]
            
            if modules_name[0] == "during_TID":
                pass
                # cmap = plt.cm.get_cmap('viridis', 15)               
                # sc = ax.scatter(xValues, value, c=self.calculate_dose(period = xValues), cmap=cmap, s=10)
                # cbar = fig.colorbar(sc, ax=ax, orientation='vertical')
                # cbar.set_label("Dose [Gray]", labelpad=1)                  
                #ax.errorbar(xValues, value, yerr=eyvalues, fmt='o', color = 'black', markerfacecolor='black', markeredgecolor="black")
        ax.legend(loc='upper left')
        #legend_handles.append(Line2D([], [], label=yLabel[number + 1]))  
        legend_handles = []
        for i, label in enumerate(ax.get_legend().get_texts()):
             handle = Line2D([0], [0], color=colors[i], label=label.get_text())
             legend_handles.append(handle)
        #
        if ymax:
            #ax.set_yticks(np.arange(ymin, ymax,steps)) 
            ax.set_ylim([ymin, ymax])
        else: 
            ax.set_yticks(np.arange(min(yMin)-1, max(yMax)+1,steps)) 
            pass
        axis_color =  cmap(3)  # Index 1 corresponds to the second color
        if yValues2:
            ax2 = ax.twinx()
            yMin2 = [0 for i in range(len(yValues2))]
            yMax2 = [0 for i in range(len(yValues2))]
            for number, value in enumerate(yValues2):
                yMin2[number] = min((y for y in value if y is not None),key=lambda x:float(x))
                yMax2[number] = max((y for y in value if y is not None),key=lambda x:float(x))
                axis_2 = ax2.plot(xValues, value, '-', color=axis_color, label = yLabel2[number+1])
                colors2 = [line.get_color() for line in ax2.get_lines()]
            ax2.legend()
            
            #legend_handles2 = []
            for i, label in enumerate(ax2.get_legend().get_texts()):
                 handle2 = Line2D([0], [0], color=colors2[i], label=label.get_text())
                 #legend_handles2.append(handle2)
                 legend_handles.extend([handle2])
        
            ax2.spines['right'].set_position(('outward', 3))  # adjust the position of the second axis     
            ax2.spines['right'].set_color(axis_color) 
            ax2.yaxis.label.set_color(axis_color)
            ax2.tick_params(axis='y', colors=axis_color)
            #legend_handles.append(Line2D([], [], color=col_row[5], label=yLabel2[number + 1]))
            ax2.set_ylabel(yLabel2[0], rotation=90, color=axis_color) 
            
            ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            if ymax2: ax2.set_ylim([1.4, 1.6]) 
            else:ax2.set_yticks(np.arange(min(yMin2)-1, max(yMax2)+2,0.5)) 
                    
        #ax.set_xticks(tick_positions) 
        if modules_name[0] == "during_TID":
            #ax1 = ax.twiny()
            #ax1.set_xlim(ax.get_xlim())
            # Set the tick positions and labels on both axes to align them
            tick_positions = np.arange(0,max(xValues),10) 
            ax.set_xticks(tick_positions)
            does_array = self.calculate_dose(period = ax.get_xticks())
            ax.set_xticklabels(does_array, rotation=0, ha='right')
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            # Adjust tick label alignment
            for tick in ax.get_xticklabels():
                tick.set_horizontalalignment('center')
            #ax1.spines['bottom'].set_position(('outward', 20))  # Adjust the distance as needed
            ax.set_ylabel(yLabel[0], rotation=90)
            ax.set_xlabel("Dose [Gray]")
        else:
            ax.set_ylabel(yLabel[0], rotation=90)
            ax.set_xlabel(xLabel) 
            tick_positions = np.arange(0,max(xValues)+2,2)
            ax.set_xticks(tick_positions)   
            
        plt.legend(handles=legend_handles, loc='upper left')
        ax.grid(True)
        #plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        fig.savefig(file_out, bbox_inches='tight')  
        #plot.tight_layout()
        PdfPages.savefig()
        #plt.xscale('log')
        plt.clf() 
        plt.close(fig)  
        return fig, ax

    def plot_ramps(self, root_dir = None, module_name="LTM8067EY-PBF", component_name="rampup", text_enable=True, PdfPages = None):
        file_in_path = root_dir+ "dc_converters/" + module_name +"/" +  component_name + "/"+module_name
        file_out_path = root_dir+ "dc_converters/" + module_name +"/" +  component_name + "/"+module_name
        fig, ax = plt.subplots()
        logger.info(f"Plotting {module_name} {component_name} Data")
        # Read the CSV file into a DataFrame, skipping the header row
        df = pd.read_csv(file_in_path+"_Rampup_results.csv", skiprows=1, header=None)
        # Extract the required columns from the DataFrame
        Usin1   = df.iloc[:, 0].astype(float)
        Tin     = df.iloc[:, 1].astype(float)
        Tout    = df.iloc[:, 2].astype(float)
    
        if text_enable: ax.set_title('Time signals at different ramp-up speeds [' + module_name + ']')
    
        ax.plot(Usin1, Tin,  label="Time of Input [$T_{In}$]")
        ax.plot(Usin1, Tout, label="Time of Output [T$_{Out}$]")
            
        ax.errorbar(Usin1, Tin, yerr=0.05*Tin, fmt='D', color = 'black', markerfacecolor='black', markeredgecolor="black")
        ax.errorbar(Usin1, Tout, yerr=0.05*Tout, fmt='o', color = 'black', markerfacecolor='black', markeredgecolor="black")
        
        ax.grid(True)
        #plt.xscale('log')
        plt.yscale('log')
        ax.set_xlabel("Ramp up Voltage rate [V/s]")
        ax.legend(loc="upper right")
        ax.set_ylabel(r'Rise Time [ms]')
        plt.tight_layout()
        plt.savefig(file_out_path +"_Rampup_results.pdf", bbox_inches='tight')
        ax.set_title('Time signals at different ramp-up speeds [' + module_name + ']')
        plt.tight_layout()
        PdfPages.savefig()
        plt.clf() 
        plt.close(fig)

    def mopshub_cic_v4_configurations(self, data= None, output_dir = None, PdfPages= None): 
        def calculate_vcan(v_fb = 1.257, r_set= data["R_set"], r11 = 47):
            """
            Calculate VCAN using the formula:
            
            VCAN = V_FB * ((R_set + R11) / R_set)
            
            Parameters:
            v_fb (float): The feedback voltage V_FB.
            r_set (float): The resistance R_set (should not be zero to avoid division by zero).
            r11 (float): The resistance R11.
            
            Returns:
            float: The calculated VCAN value.
            """
            vcan = []
            for r in r_set:
                vcan =np.append(vcan, v_fb * ((r + r11) / r))
            return vcan

        logger.info("Plotting Pattern configurations vs VCAN output for CIC v4")
        fig, ax = plt.subplots()
        value_int = np.arange(0,len(data["U-VCANA"]))
        DIP_ON_int = np.arange(0,len(data["U-VCANA"]),0.5)
        vcan = calculate_vcan()
        ax.errorbar(value_int, data["DIP_OFF"], xerr=0.0, yerr=0.005, fmt='o',color="black")
        ax.errorbar(value_int, data["U-VCANA"], xerr=0.0, yerr=0.005, fmt='o',color="black")
        # Connect the points with lines
        plt.plot(value_int, data["U-VCANA"], linestyle='-', label='DIP switch ON')
        plt.plot(value_int, data["DIP_OFF"], linestyle='-', label='DIP switch OFF')
        #plt.plot(value_int[1:],vcan, linestyle='-', color = "red", label='VCAN$_{Theo}$')
        
        # Convert the x-axis ticks to hexadecimal
        hex_labels = data["Value"] #[hex(int(value)).upper() for value in data["Value"]]
        ax.set_xticks(value_int)
        ax.set_yticks(DIP_ON_int)
        ax.set_xticklabels( hex_labels, rotation=45)  # Rotate labels for readability
        ax.set_ylim(0,max(data["U-VCANA"])+1)
        ax.grid(True)
        ax.legend() 
        ax.set_xlabel("Dual Pit Pattern[Hex]")
        ax.set_ylabel("VCAN [V]")
    
        # Create a gray region between 1.5V and 2V for MOPS opertation
        gray_region = (1.5, 2)
        #ax.fill_between(value_int, gray_region[0], gray_region[1], color='gray', alpha=0.2, label='MOPS operation')
        #plt.axhline(y=gray_region[0], linewidth=1, color='#d62728', linestyle='dashed')
        #plt.axhline(y=gray_region[1], linewidth=1, color='#d62728', linestyle='dashed')
        # Create a secondary y-axis for numbers 1 to 8
        ax2 = ax.twiny()
        # ax2.set_xlim(ax.get_xlim())
        # second_x_values = np.arange(1, 9)
        # ax2.set_xticks(value_int)  # Same positions as the first x-axis
        # ax2.set_xlabel("DIP Switch Pole", labelpad=10)
        # second_x_labels = [str(val) for val in second_x_values]
        # ax2.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
        # ax2.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
        # ax2.spines['bottom'].set_position(('outward', 55))
        plt.tight_layout()
        plt.savefig(output_dir + "mopshub_cic_v4_configurations.pdf", bbox_inches='tight')  
        ax.set_title('Pattern configurations vs VCAN output for CIC v4')
        plt.tight_layout()
        PdfPages.savefig()
        plt.clf() 
        plt.close(fig)  
    
    
    def mopshub_cic_v4_configurations_seu(self, data= None,data_seu =None,  output_dir = None, PdfPages= None): 
        logger.info("Plotting VCAN output for CIC v4 after bit flipping ")
        fig, ax = plt.subplots()
        bit_values_bin = np.arange(0,len(data_seu["Unflipped"].keys()))
        for key in data_seu.keys():
            voltage    =  [value for value in data_seu[key].values()]
            ax.scatter(bit_values_bin, voltage,marker='o', s=50) 
            hex_labels = [hex(int(value)).upper() for value in data_seu["Unflipped"].keys()]
            if key =="Unflipped": 
                plt.plot(bit_values_bin, voltage, linestyle='-', label=key)
                #plt.fill_between(bit_values_bin, data_seu["Unflipped"].values(), alpha=0.1)
            else: plt.plot(bit_values_bin, voltage, linestyle='--', label=key)
    
            ax.set_xticks(bit_values_bin)
            ax.set_xticklabels( hex_labels, rotation=45)  # Rotate labels for readability
            
            ax.grid(True)
            ax.legend() 
            ax.set_xlabel("Dual Pit Pattern[Hex]")
            ax.set_ylabel(r"VCAN [V]")
            
        plt.tight_layout()
        plt.savefig(output_dir + "mopshub_cic_v4_configurations_seu.pdf", bbox_inches='tight')  
        ax.set_title(r"VCAN output for CIC v4 after bit flipping ")
        plt.tight_layout()
        PdfPages.savefig()
        plt.clf() 
        plt.close(fig)    
        return None
    
    
    def mopshub_cic_v4_resistance(self, data= None, output_dir = None, PdfPages= None): 
        logger.info(r"Plotting RSET vs VCAN output for CIC v4")
        fig, ax = plt.subplots()
        
        value_int = np.arange(0,len(data["U-VCANA"]))
        ax.scatter( value_int[1:], data["R_set"][:-1],marker='o', s=50) 
        plt.plot(value_int[1:], data["R_set"][:-1], linestyle='-', label='Reset value')
         # Convert the x-axis ticks to hexadecimal
        hex_labels = data["Value"][1:] #[hex(int(value)).upper() for value in data["Value"][1:]]
        ax.set_xticks(value_int[1:])
        ax.set_xticklabels( hex_labels, rotation=45)  # Rotate labels for readability
        
        ax.grid(True)
        ax.legend() 
        ax.set_xlabel("Dual Pit Pattern[Hex]")
        ax.set_ylabel(r"$R_{\mathrm{set}} $[$k\Omega$]")
        
        plt.tight_layout()
        #plt.show()
        plt.savefig(output_dir + "mopshub_cic_v4_resistance.pdf", bbox_inches='tight')  
        ax.set_title(r"$R_{\mathrm{set}}$ vs VCAN output for CIC v4")
        plt.tight_layout()
        PdfPages.savefig()
        plt.clf() 
        plt.close(fig)  
        
    def mopshub_cic_v4_configuations_all(self, data= None, data_all = None, output_dir = None, PdfPages= None): 
        logger.info((r"VCAN output for CIC v4 of all possible configurations "))
        fig, ax = plt.subplots()
        ideal_points = np.arange(0,256)
     # Create a new data_all dictionary with all ideal points
        new_data_all = {
            "all": {point: data_all["all"].get(point, 0) for point in ideal_points}
        }
    
        all_points     = list(data_all["all"].keys())
        all_voltage    =  [value for value in data_all["all"].values()]
        ax.scatter(all_points, all_voltage,color= "red",marker='o',label="All Patterns", s=20)  
        # Create a scatter plot for the common points
        data["Value"] = [int(value,16) for value in data["Value"][:]]
        common_values = [value for value in list(data_all["all"].keys()) if value in list(data["Value"])]
        common_values_sorted = sorted(common_values)
        #common_values_hex= [hex(int(value)).upper() for value in common_values_sorted]
        # Create a mask array to filter common points
        ax.scatter(common_values_sorted, data["U-VCANA"][1:],marker="o")
        plt.plot(common_values_sorted, data["U-VCANA"][1:], linestyle='-', label="Valid Patterns")
        
        #plt.fill_between(common_values_sorted, data["DIP_ON"][1:],color='gray', alpha=0.2)
         # Convert the x-axis ticks to hexadecimal
        hex_labels = [hex(int(value)).upper() for value in data_all["all"].keys()]
        ax.set_xticks(all_points)
        ax.set_xticklabels( hex_labels, rotation=45)  # Rotate labels for readability
    
        ax.grid(True)
        ax.legend() 
        ax.set_xlabel("Dual Pit Pattern[Hex]")
        ax.set_ylabel(r"VCAN [V]")
        
        plt.tight_layout()
        plt.savefig(output_dir + "mopshub_cic_v4_configuations_all.pdf", bbox_inches='tight')
        ax.set_title(r"VCAN output for CIC v4 of all possible configurations") 
        plt.tight_layout()
        PdfPages.savefig()
        plt.clf() 
        plt.close(fig)    
    
            
    def close(self, PdfPages=False):
            PdfPages.close()