########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.08.2023
"""
########################################################

import sys
import os
from validators import length
import seaborn as sns
from collections import deque
import numpy as np
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tests_lib.analysis_utils      import AnalysisUtils
from tests_lib.logger_main   import Logger
from tests_lib.plotting   import Plotting
import logging
from collections import Counter
import pandas as pd
import csv
import matplotlib
from scipy import interpolate
import matplotlib.image as image
import math
log_format = '%(log_color)s[%(levelname)s]  - %(name)s -%(message)s'
log_call = Logger(log_format=log_format, name="DC\DC", console_loglevel=logging.INFO, logger_file=False)
logger = log_call.setup_main_logger()#

rootdir = os.path.dirname(os.path.abspath(__file__))
root_dir = rootdir + "/"
output_dir = "/data_files/"
import os
os.environ["NUMEXPR_MAX_THREADS"] = "4"  # Set the number of threads to 4
import numexpr as ne
from tests_lib.plot_style import *

text_enable = False

def calculate_efficiency_errors(Uout, Iout, Uin, Iin, eUout, eIout, eIin):
    # Calculate efficiency
    efficiency = (Uout * Iout * 100) / (Uin * Iin)
    efficiency[efficiency.isnull()] = 0  # Replace NaN values with 0
    # Calculate partial derivatives of efficiency with respect to each variable
    d_epsilon_d_Uout = (Iout * 100) / (Uin * Iin)
    d_epsilon_d_Iout = (Uout * 100) / (Uin * Iin)
    d_epsilon_d_Uin = (-Uout * Iout * 100) / (Uin ** 2 * Iin)
    d_epsilon_d_Iin = (-Uout * Iout * 100) / (Uin * Iin ** 2)
    
    # Calculate error on efficiency using error propagation
    delta_epsilon = np.sqrt(
        (d_epsilon_d_Uout * eUout)**2 +
        (d_epsilon_d_Iout * eIout)**2 +
        (d_epsilon_d_Uin * np.std(Uin))**2 +
        (d_epsilon_d_Iin * eIin)**2
    )
    
    # Calculate power
    power = Uout * Iout*0.001
    
    # Calculate error on power using error propagation
    delta_power = np.sqrt(
        (Iout * eUout)**2 +
        (Uout * eIout)**2
    )*0.001
    
    return efficiency, delta_epsilon, power, delta_power

def load_data(data_file = None,module_name = None, component_name = None, file_name =None ):
    data_frame = pd.read_csv(data_file, skiprows=[1])
    logger.info(f"Analyzing {module_name} {component_name} Data")    
    # logger.info the headers
    
    df_headers = data_frame.columns.tolist()
    data_frame = AnalysisUtils().check_last_row(data_frame = data_frame,column = df_headers[-1])
    return data_frame, df_headers

def extract_data_info(data_file = None,module_name = None, component_name = None, file_name = None, min_scale = None):
    data_frame, df_headers = load_data(data_file = data_file, module_name = module_name,component_name = component_name, file_name =file_name) 
    #data_frame.apply(pd.to_numeric, errors='coerce')

    day, unique_days = AnalysisUtils().getDay(data_frame.TimeStamp)
    hours, unique_hours,unique_minutes = AnalysisUtils().getHours(TimeStamps = data_frame.TimeStamp, min_scale =min_scale, device = "power_card")
    hourlyAverageValues = [0 for i in range(len(df_headers))]
    hourlySTDValues = [0 for i in range(len(df_headers))]
    new_headers = []
    for pos,column in enumerate(df_headers):
        if pos > 0 and pos < len(df_headers):
            hourlyAverageValues[pos-1], hourlySTDValues[pos-1] = AnalysisUtils().get_hourly_average_value(data_frame = data_frame , 
                                                                                  column = column,
                                                                                  unique_days = unique_days)
            
            new_headers = np.append(new_headers, column)
    
    return data_frame, new_headers,hourlyAverageValues, hourlySTDValues,day, unique_days

 
        
def extract_time_info(data_file = None,module_name = None, component_name = None, file_name = None, min_scale = None):
    data_frame, df_headers = load_data(data_file = data_file, module_name = module_name,component_name = component_name, file_name =file_name)
    #try: 
    day, unique_days = AnalysisUtils().getDay(data_frame.TimeStamp)
    #except: day = 0
    hours, unique_hours = AnalysisUtils().getHours(TimeStamps = data_frame.TimeStamp, min_scale =min_scale, device = "power_card")
    hourlyAverageValues = [0 for i in range(len(df_headers))]
    new_headers = []

    for pos,column in enumerate(df_headers):
        if pos > 0 and pos < len(df_headers):
            hourlyAverageValues[pos-1] = AnalysisUtils().getHourlyAverageValue(hours = hours,data = data_frame[column], min_scale = min_scale, unique_hours = unique_hours, unique_days = unique_days)   
            new_headers = np.append(new_headers, column)
    return data_frame, new_headers,hourlyAverageValues,day, unique_days
        
def load_power_data(data_file = None,module_name = None, component_name = None, file_name = None,min_scale = None):
    
    data_frame, new_headers,hourlyAverageValues, hourlySTDValues,day, unique_days = extract_data_info(data_file = data_file, module_name = module_name,component_name = component_name, file_name =file_name, min_scale = min_scale)
    f = 1000  # to convert to mA

        
    time      = data_frame.iloc[:, 0].astype(str)
    elabsed   = data_frame.iloc[:, 1].astype(float)

    Usin1  = data_frame.iloc[:, 2].astype(float)
    Iin1   = data_frame.iloc[:, 6].astype(float) * f
    eIin1  = data_frame.iloc[:, 7].astype(float) * f
    Uout1  = data_frame.iloc[:, 10].astype(float)
    eUout1 = data_frame.iloc[:, 11].astype(float)
    Iout1  = data_frame.iloc[:, 14].astype(float) * f
    eIout1 = data_frame.iloc[:, 15].astype(float) * f
    Uin1   = data_frame.iloc[:, 18].astype(float) 
    
    # Calculate means
    mean_Usin1 = np.mean(Usin1)
    mean_Uout1 = np.mean(Uout1)
    mean_Iout1 = np.mean(Iout1)
    mean_Uin1 = np.mean(Uin1)
    mean_Iin1 = np.mean(Iin1)
    mean_eUout1 = np.mean(eUout1)
    mean_eIout1 = np.mean(eIout1)
    mean_eIin1 = np.mean(eIin1)
    # Calculate standard deviations
    std_Usin1 = np.std(Usin1, ddof=1)
    std_Uout1 = np.std(Uout1, ddof=1)
    std_Iout1 = np.std(Iout1, ddof=1)
    std_Uin1 = np.std(Uin1, ddof=1)
    std_Iin1 = np.std(Iin1, ddof=1)
    std_eUout1 = np.std(eUout1, ddof=1)
    std_eIout1 = np.std(eIout1, ddof=1)
    std_eIin1 = np.std(eIin1, ddof=1)
    
    
    # Print the results
    logger.report(f"Mean of Usin1: {mean_Usin1:.3f}, Standard Deviation: {std_Usin1:.3f}")
    logger.report(f"Mean of Uin1: {mean_Uin1:.3f}, Standard Deviation: {std_Uin1:.3f}")
    logger.report(f"Mean of Uout1: {mean_Uout1:.3f}, Standard Deviation: {std_Uout1:.3f}")
    logger.report(f"Mean of Iout1: {mean_Iout1:.3f}, Standard Deviation: {std_Iout1:.3f}")
    
    logger.report(f"Mean of Iin1: {mean_Iin1:.3f}, Standard Deviation: {std_Iin1:.3f}")
    logger.report(f"Mean of eUout1: {mean_eUout1:.3f}, Standard Deviation: {std_eUout1:.3f}")
    logger.report(f"Mean of eIout1: {mean_eIout1:.3f}, Standard Deviation: {std_eIout1:.3f}")
    logger.report(f"Mean of eIin1: {mean_eIin1:.3f}, Standard Deviation: {std_eIin1:.3f}")
    
    efficiency, delta_epsilon, P_out, eP_out = calculate_efficiency_errors(Uout1, Iout1, Usin1, Iin1, eUout1, eIout1, eIin1)
    #Get Hourly average effeciencyUin1
    data_frame["efficiency"] = efficiency
    data_frame["power"] = P_out
    data_frame["delta_epsilon"] = delta_epsilon
    data_frame["e_power"] = eP_out    
    efficiency_average,_ = AnalysisUtils().get_hourly_average_value(data_frame = data_frame , 
                                                                      column = "efficiency",
                                                                      unique_days = unique_days)

    P_out_average, _ = AnalysisUtils().get_hourly_average_value(data_frame = data_frame , 
                                                                      column = "power",
                                                                      unique_days = unique_days)
    
    delta_epsilon_average, _ = AnalysisUtils().get_hourly_average_value(data_frame = data_frame , 
                                                                      column = "delta_epsilon",
                                                                      unique_days = unique_days)

    eP_out_average, _ = AnalysisUtils().get_hourly_average_value(data_frame = data_frame , 
                                                                      column = "e_power",
                                                                      unique_days = unique_days)
                    
    hours, unique_hours,unique_minutes = AnalysisUtils().getHours(TimeStamps = data_frame.TimeStamp, min_scale =min_scale, device = "power_card")
    
    #efficiency_average = AnalysisUtils().getHourlyAverageValue(hours = hours,data = efficiency, min_scale = min_scale, unique_hours = unique_hours, unique_days = unique_days)
    #P_out_average = AnalysisUtils().getHourlyAverageValue(hours = hours,data = P_out, min_scale = min_scale, unique_hours = unique_hours, unique_days= unique_days)
    
    if min_scale == "min_scale": period = np.arange(60) 
    else:  period = np.arange(len(unique_hours))
    
    return hours, Usin1, Uin1, Uout1, eUout1, Iin1, eIin1, Iout1, eIout1,efficiency,delta_epsilon,P_out,eP_out, efficiency_average,P_out_average,delta_epsilon_average, eP_out_average ,new_headers,hourlyAverageValues, hourlySTDValues,day, period


def plot_mopshub_powercard_tid_results(modules_name=None, files_name = None, component_name = None,min_scale = None, parameters = None): 
    if isinstance(files_name, str):
        files_name = [files_name]  # Convert single file to list
        top_level = True
    else: top_level = False 
    
    if isinstance(modules_name, str): modules_name = [modules_name]  # Convert single file to list
    else: modules_name = modules_name
    
    def select_headers_by_indices(headers,hourlyAverageValues, indices):
        selected_headers = [headers[i] for i in indices if 0 <= i < len(headers)]
        selected_data = [hourlyAverageValues[i] for i in indices if 0 <= i < len(hourlyAverageValues)]
        return selected_headers ,selected_data  
     
    for index, (file_name, module_name) in enumerate(zip(files_name, modules_name)):
        file_in_path = component_name+"/" 
        data_file = file_in_path + file_name+".csv"
        #file_out_path = file_in_path + file_name+".pdf"      
        #data_frame, new_headers,hourlyAverageValues,day = extract_time_info(data_file = data_file, module_name = module_name,component_name = component_name, file_name =file_name, min_scale = min_scale)  
        hours, Usin1, Uin1, Uout1, eUout1, Iin1, eIin1, Iout1, eIout1, efficiency,delta_epsilon,P_out,eP_out, efficiency_average,P_out_average,delta_epsilon_average, eP_out_average , new_headers,hourlyAverageValues,hourlySTDValues,day, period = load_power_data(data_file =data_file,
                                                                                                                                                                                                                       module_name = module_name, 
                                                                                                                                                                                                                       component_name = component_name,
                                                                                                                                                                                                                       file_name = file_name, min_scale = min_scale) 
        
        xLabel  = f"Time [{min_scale[:-6]}]" 
        
        figName = (str(day)+"_fig_all")
        plt.figure(figName)
        for col_index, parameter in enumerate(parameters):
            #ax = axes[col_index, col_index]
            #ax.set_title(parameter)  # Set subplot title
            logger.info(f"Plotting TID Results {modules_name} for data in {file_name}.csv [{min_scale}/{parameter}]")
            
            if parameter == "supply":
            # #Plot coupler voltages
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [1,17])
                _ , eyValues = select_headers_by_indices(new_headers,hourlySTDValues, [1, 17])
                selected_headers2 , yValues2 = select_headers_by_indices(new_headers,hourlyAverageValues, [5])
                
                yLabel  = ["Input Voltage $V_{in}$ [V]"]+selected_headers
                yLabel2  = ['Input Current [A]']+selected_headers2
                fig_isin1, ax_isin1 = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          eyValues = eyValues,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          min_scale = min_scale,
                                                          ymax = 20, ymin= 0, 
                                                          title = f'Measured Supply {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          steps = 0.04,
                                                          modules_name = modules_name,
                                                          yValues2 = yValues2,
                                                          yLabel2= yLabel2,
                                                          file_out = f"{data_file[:-4]}_{modules_name}"+"_supply.pdf",
                                                          PdfPages = PdfPages)             
            elif parameter == "all":
                #Plot Usin1, Uin1
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [1,17,9])
                _ , eyValues = select_headers_by_indices(new_headers,hourlySTDValues, [1, 17,9])
                selected_headers2 , yValues2 = select_headers_by_indices(new_headers,hourlyAverageValues, [13])
                
                yLabel  = ["Voltage [V]"]+["U$_{supply}$(In) [V]", "V$_{PP3}$(In) [V]", "V$_{FPGA}$(Out) [V]"]#selected_headers
                yLabel2  = ['Current [A]']+["I$_{FPGA}$(Out) [A]"]
                fig_Usin1, ax_Usin1 = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          eyValues = eyValues,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          min_scale = min_scale,
                                                          ymax = None, ymin= 0, 
                                                          title = f'Measured Channels {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          modules_name = modules_name,
                                                          yValues2 = yValues2,
                                                          yLabel2= yLabel2,   
                                                          ymax2 = True,                                                           
                                                          steps = 2,
                                                          file_out = f"{data_file[:-4]}_{modules_name[index]}"+"_all.pdf",
                                                          PdfPages = PdfPages)
                
            elif parameter == "Usin1":
                #Plot Usin1, Uin1
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [1,17])
                _ , eyValues = select_headers_by_indices(new_headers,hourlySTDValues, [1, 17])
                yLabel  = ["Voltage (V)"]+["U$_{supply}$ (In) [V]", "V$_{PP3}$  (In) [V]"]#selected_headers
                fig_Usin1, ax_Usin1 = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          eyValues = eyValues,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          min_scale = min_scale,
                                                          ymax = None, ymin= 0, 
                                                          title = f'Input voltage {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          modules_name = modules_name,
                                                          steps = 0.5,
                                                          file_out = f"{data_file[:-4]}_{modules_name[index]}"+"_Uin.pdf",
                                                          PdfPages = PdfPages)
            
            

            elif parameter == "full":
                #Plot full 
                xValues = np.arange(0,len(Usin1))
                yValues = [Usin1]
                yLabel  = ["Voltage [V]"]+["Usin1"]
            
                fig_full, ax_full = Plotting().plot_data(xValues = xValues,
                                                          yValues = yValues,
                                                          eyValues = [0],
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          min_scale = min_scale,
                                                          title = f'Input voltages {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          modules_name = modules_name, 
                                                          steps = 0.04,
                                                          file_out = f"{data_file[:-4]}_{modules_name[index]}"+"_full.pdf",
                                                          PdfPages = PdfPages)
                
            elif parameter == "Uout1":
                #Plot Uout1
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [9])
                selected_headers2 , yValues2 = select_headers_by_indices(new_headers,hourlyAverageValues, [13])
                _ , eyValues = select_headers_by_indices(new_headers,hourlySTDValues, [9])
                
                yLabel  = ["Voltage [V]"]+["V$_{FPGA}$ (Out) [V]"]
                yLabel2  = ["Current [A]"]+["I$_{FPGA}$ (Out) [A]"]       
                fig_out, ax_out = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          eyValues = eyValues,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          min_scale = min_scale,
                                                          ymax = 5.2,
                                                          ymin= 4.8, 
                                                          title = f'Output voltage {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          modules_name = modules_name,
                                                          steps = 0.05,
                                                          yValues2 = yValues2,
                                                          yLabel2= yLabel2,                                                          
                                                          file_out = f"{data_file[:-4]}_{modules_name[index]}"+"_Uout.pdf",
                                                          PdfPages = PdfPages)
                

                
                fig_out_hist, ax_out_hist = Plotting().plot_histogram(xValues = Uout1, 
                                                                      zValues = hours,
                                                                    xlabel=yLabel[1], 
                                                                    modules_name= modules_name,
                                                                    ylabel="# Measurements ", #'$\\Delta$ VCAL'
                                                                    title=f'Output voltages {modules_name}', 
                                                                    bins=20, 
                                                                    file_out=f"{data_file[:-4]}_{modules_name[index]}"+"_Uout_hist.pdf", 
                                                                    PdfPages=PdfPages)
            
            elif parameter == "efficiency":
                #Plot efficiency
                selected_headers , yValues = ["%"], [efficiency_average]

                yLabel  = ["Efficiency %"]+selected_headers
                fig_eff, ax_eff = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          eyValues = delta_epsilon_average,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          ymax = 100, ymin= 0, 
                                                          min_scale = min_scale,
                                                          title = f'Efficiency {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          modules_name = modules_name,
                                                          steps = 5,
                                                          file_out = f"{data_file[:-4]}_{modules_name[index]}"+"_efficiency.pdf",
                                                          PdfPages = PdfPages)
            
            elif parameter == "power":
                #Plot power
                selected_headers , yValues = ["W"], [P_out_average]
                yLabel  = ["Power [W]"]+selected_headers
                fig_power, ax_power = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          ymax = 10, ymin= 0, 
                                                          min_scale = min_scale,
                                                          title = f'Power {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          modules_name = modules_name, 
                                                          steps = 5,
                                                          file_out = f"{data_file[:-4]}_{modules_name[index]}"+"_power.pdf",
                                                          PdfPages = PdfPages)
                
        plt.tight_layout()  # Adjust subplot layout
        plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.4)
        #plt.savefig(f"{data_file[:-4]}_{label}"+"_all.pdf")   
    print("--------------------------------------------------------------------------------------------------------")                      

def plot_parameters_dcconverter(modules_name=None, files_name=None, component_name = None,a = 8, text_enable =  None,result_dir = None, legends =None):
    logger.info(f"Plotting Test Results {modules_name}")
    if isinstance(files_name, str):
        files_name = [files_name]  # Convert single file to list
        top_level = True
    else: top_level = False 
    
    if isinstance(modules_name, str): modules_name = [modules_name]  # Convert single file to list
    else: modules_name = modules_name
    
    fig1, ax1 = plt.subplots() 
    fig2, ax2 = plt.subplots() 
    fig3, ax3 = plt.subplots()
    fig4, ax4 = plt.subplots()
         
    ax1.grid(True)
    ax1.set_ylabel("$V_{Out}$ (Out) [V]")#("Output Voltage $V_{out}$[V]")
    ax1.set_xlabel("$V_{PP3}$ (In) [V]")#("Input Voltage $V_{in}$ [V]")
    ax1.autoscale(enable=True, axis='x', tight=None)
   
    

    ax2.grid(True)
    ax2.set_xlabel("$V_{PP3}$ (In) [V]")#("Input Voltage $V_{in}$ [V]")
    ax2.set_ylabel(r'Current [mA]')#(r'Current $I$ [mA]')


    ax3.grid(True)   
    ax3.set_ylabel("Efficiency [%]")
    ax3.set_xlabel("Input Voltage $V_{in}$ [V]")
    ax3.autoscale(enable=True, axis='x', tight=None)


    ax4.grid(True)
    ax4.set_xlabel("Input Voltage $V_{in}$ [V]")
    ax4.set_ylabel(r'Power consumption [W]')
    
   
    #fig, ax =  plot_data()    
    for index, (file_name, module_name) in enumerate(zip(files_name, modules_name)):
        if legends:
            legend_title = legends[index]
        else:
            legend_title = module_name
            
        file_in_path = root_dir + component_name+"/"
        data_file = file_in_path + module_name + output_dir + file_name+".csv"
        
        file_name_det = os.path.basename(data_file)
        file_directory = os.path.dirname(data_file)
        if os.path.exists(data_file): #check if the file exist 
            data_file = file_in_path + module_name + output_dir + file_name+".csv"
            if top_level : file_out_path = root_dir +component_name + "/" +module_name + "/" + file_name
            if result_dir:   file_out_path =result_dir 
            else: file_out_path = root_dir +component_name + "/"+component_name 
        else: 
            data_file = file_in_path + file_name+".csv"
            file_out_path = data_file[:-4]+".pdf"   
        hours, Usin1, Uin1, Uout1, eUout1, Iin1, eIin1, Iout1, eIout1,efficiency,delta_epsilon,P_out,eP_out, _,_, _,_,_,_,_ ,_,_  = load_power_data(data_file =data_file,module_name = module_name, component_name = component_name,file_name = file_name)  
        logger.info(f"Output results in: {file_out_path}...")
        if text_enable: 
            if module_name == "before_neutron" or module_name == "after_neutron" or module_name == "compare_tests" : title_name = file_name[0:10]
            else: title_name = module_name 
            ax1.set_title(f"Test Results [{title_name}, {modules_name[0]}]")  
            ax2.set_title(f"Test Results [{title_name}, {modules_name[0]}]") 
            ax3.set_title(f"Efficiency Results [{title_name}, {modules_name[0]}]")  
            ax4.set_title(f"Test Results [{title_name}, {modules_name[0]}]")    
        if top_level : 
            
            ax1.errorbar(Uin1, Uout1, yerr=eUout1, color="black", fmt='o' , markerfacecolor='black', markeredgecolor='black')
            ax1.plot(Uin1, Uout1, label=f"Output Voltage [{legend_title}]")   
            # plot_data(xValues = Uin1, yValues= Uout1,
            #           eyValues= eUout1, 
            #           xLabel= "Input Voltage $V_{in}$ [V]", 
            #           yLabel=  "Output Voltage $V_{out}$[V]",
            #           Label = f"{legend_title}",
            #           title = f"Testing Results of the {legend_title}",
            #           file_out = file_out_path+ "_voltage.pdf")               
            
            #ax2.errorbar(Uin1, Iin1 , yerr=eIin1 , color="black", fmt='D', markerfacecolor='black', markeredgecolor="black")
            #ax2.errorbar(Uin1, Iout1, yerr=eIout1, color="black", fmt='o', markerfacecolor='black', markeredgecolor="black")
            
            ax2.plot(Uin1, Iin1, color = col_row[8],label=f"Input Current [{legend_title}]")
            ax2.plot(Uin1, Iout1, label=f"Output Current [{legend_title}]")
            spline = interpolate.splrep(Usin1[a:], efficiency[a:], s=5, k=2)  # create spline interpolation
            
            xnew = np.linspace(np.min(Usin1[a:]), np.max(Usin1[a:]), num=50, endpoint=True)
            spline_eval = interpolate.splev(xnew, spline)  # evaluate spline
            ax3.errorbar(Usin1[a:], efficiency[a:], color="black", fmt='o' , markerfacecolor='black', markeredgecolor='black')
            ax3.plot(xnew, spline_eval, "-", label=f"{legend_title}") 
                              
            #sc = ax4.scatter(Uin1, Iout1, c=P_out, cmap=cmap, s=10)
            #cbar = fig4.colorbar(sc, ax=ax4, orientation='vertical')
            #cbar.set_label("Power consumption [W]", labelpad=1)
            #cmap = plt.cm.get_cmap('viridis', 15)
            
            ax4.errorbar(Uin1, P_out, yerr=eP_out, color="black", fmt='o', markerfacecolor='black', markeredgecolor="black")
            ax4.plot(Uin1, P_out, label=f"{legend_title}")
            # plot_data(xValues = Uin1, yValues= P_out,eyValues= 0.0, 
            #                       xLabel= "Input Voltage $V_{in}$ [V]", 
            #                       yLabel=  r'Power consumption [W]',
            #                       Label = f"{legend_title}",
            #                       title = f"Testing Results of the {legend_title}",
            #                       file_out = file_out_path+ "_power.pdf")
        else: 
            #ax1.errorbar(Usin1, Uout1, yerr=eUout1, color="black", fmt='o' , markerfacecolor='black', markeredgecolor='black')
            ax1.plot(Usin1, Uout1, label=f"[{legend_title}]")                  
            
            #ax2.errorbar(Usin1, Iin1 , yerr=eIin1 ,fmt='D' ,color="black", markerfacecolor='black', markeredgecolor="black")
            #ax2.errorbar(Usin1, Iout1, yerr=eIout1, fmt='o', color="black", markerfacecolor='black', markeredgecolor="black")
            
            ax2.plot(Usin1, Iin1,label=f"Input Current [{legend_title}]")
            ax2.plot(Usin1, Iout1, label=f"Output Current [{legend_title}]")
            
            spline = interpolate.splrep(Usin1[a:], efficiency[a:], s=10, k=2)  # create spline interpolation
            xnew = np.linspace(np.min(Usin1[a:]), np.max(Usin1[a:]), num=50, endpoint=True)
            spline_eval = interpolate.splev(xnew, spline)  # evaluate spline
            #ax3.errorbar(Usin1[a:], efficiency[a:], color="black", fmt='o' , markerfacecolor='black', markeredgecolor='black')
            ax3.plot(xnew, spline_eval, "-", label=f"{legend_title}") 
            #ax4.errorbar(Uin1, P_out, yerr=0, color="black", fmt='o', markerfacecolor='black', markeredgecolor="black")
            ax4.plot(Usin1, P_out, label=f"{legend_title}")
                      
    ax1.set_ylim([-0.5, max(Uout1) + 1])
    ax1.legend(loc="upper left")
    plt.tight_layout()
    fig1.savefig(file_out_path+ f"{files_name[0][:3]}_voltage.png", bbox_inches='tight')   
    ax1.set_title(f"Testing Results of the {legend_title}")
    plt.tight_layout()
    PdfPages.savefig()  
    #plt.clf() 
    plt.close(fig1)

    #ax2.set_ylim([-5, max(Iout1)+500])    
    ax2.legend(loc="upper right") 
    plt.tight_layout()
    fig2.savefig(file_out_path+ f"{files_name[0][:3]}_current.png", bbox_inches='tight')
    ax2.set_title(f"Testing Results of the {legend_title}")  
    plt.tight_layout()
    PdfPages.savefig()
    #plt.clf() 
    plt.close(fig2)
    
    ax3.set_ylim([0, 110])
    ax3.legend(loc="upper left")
    plt.tight_layout()
    fig3.savefig(file_out_path+ f"{files_name[0][:3]}_efficiency.png", bbox_inches='tight')    
    ax3.set_title(f"Testing Results of the {legend_title}")
    plt.tight_layout()
    PdfPages.savefig()    
    #plt.clf() 
    plt.close(fig3)
   

    ax4.legend(loc="upper left") 
    plt.tight_layout()
    fig4.savefig(file_out_path+ f"{files_name[0][:3]}_power.png", bbox_inches='tight')  
    ax4.set_title(f"Efficiency Results of the {legend_title}")
    plt.tight_layout()
    PdfPages.savefig()    
    #plt.clf() 
    plt.close(fig4)
    print("--------------------------------------------------------------------------------------------------------")
# Main function
if __name__ == '__main__':
    # get program arguments
    PdfPages = PdfPages(root_dir+'mopshub_dcdc_converters.pdf')
    basic_tests = { 
        "dc_converters":[
                {
                    "before_neutron":[{"TDN1-2411WI_1AL/1AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1BL/1BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1AH/1AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1BH/1BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1AM/1AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1BM/1BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },
                {
                    "before_neutron":[{"NCS1S2405SC_2AL/2AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2BL/2BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2AH/2AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2BH/2BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2AM/2AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2BM/2BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },
                {
                    "before_neutron":[{"RSO-2405SZ_3AL/3AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3BL/3BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3AH/3AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3BH/3BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3AM/3AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3BM/3BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },                
                {
                    "before_neutron":[{"PG02S2405A_4AL/4AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BL/4BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AH/4AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BH/4BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AM/4AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BM/4BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },    
                {
                    "before_neutron":[{"PG02S2405A_4AL2/4AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BL2/4BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AH2/4AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BH2/4BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AM2/4AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BM2/4BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                }, 
                {
                    "before_neutron":[{"SPBW03F05_5AL/5AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5BL/5BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5AH/5AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5BH/5BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5AM/5AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5BM/5BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                }, 
                {
                    "before_neutron":[{"EC3SAW24S05P_6AL/6AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6BL/6BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6AH/6AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6BH/6BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6AM/6AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6BM/6BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },                                             
                {
                    "before_neutron":[{"TEC2-2411_7AL/7AL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7BL/7BL_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7AH/7AH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7BH/7BH_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7AM/7AM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7BM/7BM_dcdc_before_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },
                {
                    "after_neutron":[{"TDN1-2411WI_1AL/1AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1BL/1BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1AH/1AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1BH/1BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1AM/1AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TDN1-2411WI_1BM/1BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },
                {
                    "after_neutron":[{"NCS1S2405SC_2AL/2AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2BL/2BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2AH/2AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2BH/2BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2AM/2AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"NCS1S2405SC_2BM/2BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },
                {
                    "after_neutron":[{"RSO-2405SZ_3AL/3AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3BL/3BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3AH/3AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3BH/3BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3AM/3AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"RSO-2405SZ_3BM/3BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },                
                {
                    "after_neutron":[{"PG02S2405A_4AL/4AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BL/4BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AH/4AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BH/4BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AM/4AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BM/4BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },    
                {
                    "after_neutron":[{"PG02S2405A_4AL/4AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BL/4BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AH/4AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BH/4BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4AM/4AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"PG02S2405A_4BM/4BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                }, 
                {
                    "after_neutron":[{"SPBW03F05_5AL/5AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5BL/5BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5AH/5AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5BH/5BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5AM/5AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"SPBW03F05_5BM/5BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                }, 
                {
                    "after_neutron":[{"EC3SAW24S05P_6AL/6AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6BL/6BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6AH/6AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6BH/6BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6AM/6AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"EC3SAW24S05P_6BM/6BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },                                             
                {
                    "after_neutron":[{"TEC2-2411_7AL/7AL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7BL/7BL_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7AH/7AH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7BH/7BH_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7AM/7AM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]},
                                     {"TEC2-2411_7BM/7BM_dcdc_after_neutron":["Uout1", "all", "efficiency","Usin1","supply","power"]}
                                    ]
                },
                                
                {
                    "RSO-2405SZ":["5v"]
                },

                {
                    "AP64500SP-EVM": ["3.3v_AWG20","3.3v","5v"]
                },
                {
                    "LTM8067EY-PBF": ["2.6v","2.6_cables"]
                },            
                {
                    "MAXM17536ALY": ["5v"]
                }                   
            ],
         "rampup":[
                {
                    "AP64500SP-EVM":["rampup/NOCable/Wiener/20V","rampup/NOCable/Wiener/15V"]
                },         
                {
                    "LTM8067EY-PBF": ["rampup/"]
                }                   
            ],
          "power_card":[
                {
                    "card_1_v1":["power_card_test"]
                },         
                {
                    "card_2_v1":["power_card_test","cable_power_card_test"]
                },
                {
                    "card_3_v1":["power_card_test"]
                },                  
                {
                    "card_5_v2": ["power_card_test","cable_power_card_test"]
                } 
            ],
          "power_card/TID_results":[#top
                {
                "compare_tests":[#module folder
                    {"card_1_v2/card_1_v2_power_card_test":["Uout1", "all", "efficiency","Usin1","supply","power"]},                   
                    {"card_1_v2_aftertid/card_1_v2_aftertid_power_card_test":["Uout1", "all", "efficiency","Usin1","supply","power"]} 
                    ],
                "before_TID":[#module folder
                    {"card_1_v2_cable_power_card_tid":["Uout1", "all","efficiency","supply","power"]#files
                     }                 
                    ],
                "during_TID":[#module folder
                    {"card_1_v2_cable_power_card_tid":["Uout1", "all", "efficiency","Usin1","power"]#files
                     }                   
                    ],                
                "after_TID":[#module folder
                    {"card_1_v2_cable_power_card_tid":["Uout1", "all", "efficiency","Usin1","supply","power"]#files
                     }                   
                    ]               
                }
            ],               
          "power_card/neutron_results":[#top
                {
                "before_radiation":[#module folder
                    {"card_3_v2_cable_beforeneutron_power_card_longtime":["Uout1", "all", "efficiency","Usin1","supply","power"]#files
                     }                                   
                    ],                
                "after_irradiation":[#module folder
                    {"card_3_v2_cable_afterneutron_power_card_longtime":["Uout1", "all", "efficiency","Usin1","supply","power"]#files
                     }                                   
                    ]    
                }
            ] 
        }     
   
                              
    if len(sys.argv) > 1:
       logger.notice(f"Processing Data files...")                 
       files_arg =  [f for f in range(len(sys.argv))]
       for number, file in enumerate(sys.argv[1:]):
            logger.notice(f"Opening {file}")
            file_directory = os.path.dirname(file)
            # Get file name
            file_name = os.path.basename(file)
            plot_mopshub_powercard_tid_results(modules_name="card_1_v2",
                                                 files_name= file_name[:-4], # remove .csv
                                                 component_name = file_directory,
                                                 min_scale = "h_scale",
                                                 parameters = ["Uout1","Usin1","Isin1","power", "efficiency"]) 
    else: 
        logger.warning(f"No argument Provided. Plotting Stored data")            
    #     neutron_tests_top = "power_card/neutron_results"#next(iter(basic_tests))#get top 
    #     modules_name = []
    #     for ic in basic_tests[neutron_tests_top]: modules_name.extend(list(ic.keys()))   
    #     for ic in basic_tests[neutron_tests_top]:
    #          for m in ic:# get module folder
    #             for t in ic[m]:
    #                 for p in t: #get files
    #                     file = f"{neutron_tests_top}/{m}/{p}.csv"
    #                     file_directory = os.path.dirname(file)
    #                     file_name = os.path.basename(file)
    #                     plot_mopshub_powercard_tid_results(modules_name=m,
    #                                                     files_name= file_name[:-4], # remove .csv
    #                                                     parameters =t[p],
    #                                                     component_name = file_directory,
    #                                                     min_scale = "h_scale")
    # #
    # tid_tests_top = "power_card/TID_results"#next(iter(basic_tests))#get top 
    # modules_name = []
    # for ic in basic_tests[tid_tests_top]: modules_name.extend(list(ic.keys()))  
    # for ic in basic_tests[tid_tests_top]:
    #      for m in ic:# get module folder
    #         for t in ic[m]:
    #             for p in t: #get files
    #                 if m == "compare_tests":
    #                     files_compare = [list(d.keys())[0] for d in ic[m]]
    #                     component_name = "power_card/TID_results"
    #                     file_directory = f"{tid_tests_top}/{m}/"
    #                     plot_parameters_dcconverter(modules_name=[m,m],
    #                                                  files_name=files_compare,
    #                                                  legends= ["Before TID","After TID"],
    #                                                  result_dir = file_directory,
    #                                                  component_name = component_name, a =6) 
    #                 else:    
    #                     file = f"{tid_tests_top}/{m}/{p}.csv"
    #                     file_directory = os.path.dirname(file)
    #                     file_name = os.path.basename(file)
    #                     plot_mopshub_powercard_tid_results(modules_name=m,
    #                                                     files_name= file_name[:-4], # remove .csv
    #                                                     parameters =t[p],
    #                                                     component_name = file_directory,
    #                                                     min_scale = "h_scale")        
    # #
    # # #Plot data for Magnetic Field
    # modules_compare = ['magnetic_field_results/card_4_v2_magnetic_0_power_card_test',
    #                    "magnetic_field_results/card_4_v2_magnetic_45_power_card_test",
    #                    "magnetic_field_results/card_4_v2_magnetic_90_power_card_test"]
    # files_compare =  ["magnetic_field_results/card_4_v2_magnetic_0_power_card_test/card_4_v2_magnetic_0_power_card_test",
    #                   "magnetic_field_results/card_4_v2_magnetic_45_power_card_test/card_4_v2_magnetic_45_power_card_test",
    #                   "magnetic_field_results/card_4_v2_magnetic_90_power_card_test/card_4_v2_magnetic_90_power_card_test"]
    
    # component_name = "power_card"
    # result_dir = root_dir +component_name + "/magnetic_field_results/magnetic_field_results_"+component_name
    # #Plotting().analyze_magenteic_field(file_out = result_dir)
    # plot_parameters_dcconverter(modules_name=modules_compare,
    #                              files_name=files_compare,
    #                              legends= ["0$^o$","45$^o$","90$^o$"],
    #                              result_dir = result_dir,
    #                              component_name = component_name, a =10)  
    #
    # #Plot Several Files Together
    # modules_name = []
    # for ic in basic_tests["power_card"]: modules_name.extend(list(ic.keys()))   
    # files_name =  [m+"_power_card_test" for m in modules_name]
    # plot_parameters_dcconverter(modules_name=modules_name[1:],
    #                              files_name=files_name[1:],
    #                              component_name = "power_card", a =6)  
    
    ##Plot individual components
    # for ic in basic_tests["power_card"]:
    #      for m in ic:
    #        for t in ic[m]:
    #         plot_parameters_dcconverter(modules_name=m,
    #                                  files_name=m+"_"+t,
    #                                  component_name = "power_card", a =6)  
    #
    #
    # for r in basic_tests["rampup"]:
    #      for m in r:
    #        for test in r[m]:
    #         Plotting().plot_ramps(module_name=m,
    #                               root_dir = root_dir,
    #                              text_enable=False,
    #                              component_name = test, PdfPages=PdfPages )
    
    #modules_name = []
    #for ic in basic_tests["dc_converters"]: 
    #    modules_name.extend(list(ic.keys())) 
    basic_tests_top = "dc_converters"
    for ic in basic_tests[basic_tests_top]:

    #                 for p in t: #get files
    #                     if m == "compare_tests":
         for m in ic:# get module folder
           for voltage in ic[m]:
                #if isinstance(voltage, str):
                    # for p in t: #get files
                
                if m == "before_neutron" or m == "after_neutron"  :
                    files_compare = [list(d.keys())[0] for d in ic[m]]
                    
                    component_name = basic_tests_top
                    
                    file_directory = f"{basic_tests_top}/{m}/"
                    
                    plot_parameters_dcconverter(modules_name=[m,m,m,m,m,m],
                                                 files_name=files_compare,
                                                 legends= ["AL","BL","AH","BH","AM","BM"],
                                                 result_dir = file_directory,
                                                 text_enable = True,
                                                 component_name = component_name,
                                                  a =6) 
                else:    
                    plot_parameters_dcconverter(modules_name=m,
                                             files_name=m+"_"+voltage,
                                             component_name = basic_tests_top)
    PdfPages.close()