########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.08.2023
"""
########################################################

import datetime 
import sys
import time
import pandas as pd
import numpy as np
import yaml
from matplotlib import pyplot as plt
from tests_lib.analysis_utils      import AnalysisUtils
from tests_lib.logger_main   import Logger
from tests_lib.plotting   import Plotting
from tests_lib.plot_style import *

import logging
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import os
log_format = '%(log_color)s[%(levelname)s]  - %(name)s -%(message)s'
log_call = Logger(log_format=log_format, name="Analysis", console_loglevel=logging.INFO, logger_file=False)
logger = log_call.setup_main_logger()#
rootdir = os.path.dirname(os.path.abspath(__file__))
root_dir = rootdir+"/"

def load_data(data_file = None,module_name = None, component_name = None):
    data_frame = pd.read_csv(data_file, skiprows=[1],skipfooter=2,engine='python')
    logger.info(f"Loading {module_name} {component_name} Data")    
    # logger.info the headers
    df_headers = data_frame.columns.tolist()
    data_frame = AnalysisUtils().check_last_row(data_frame = data_frame, column = df_headers[-1])
    return data_frame, df_headers

def load_cic_data(data_file = None,module_name = None, component_name = None, file_name = None,min_scale = None):
    data_frame, df_headers = load_data(data_file = data_file, module_name = module_name,component_name = component_name) 
    try: data_frame.TimeStamp
    except : data_frame["TimeStamp"] = data_frame.iloc[:, 0]
    day, unique_days = AnalysisUtils().getDay(data_frame.TimeStamp)
    
    hours, unique_hours, unique_minutes = AnalysisUtils().getHours(TimeStamps = data_frame.TimeStamp, min_scale =min_scale,device = "cic_card")
    
    hourlyAverageValues = [0 for i in range(len(df_headers))]
    hourlySTDValues = [0 for i in range(len(df_headers))]
    new_headers = []
    mean_values = data_frame.mean()
    std_dev_values = data_frame.std()
    
    logger.report(f"Mean = {mean_values}")
    logger.report(f"SD = {std_dev_values}")
    for pos,column in enumerate(df_headers):
        if pos > 0 and pos < len(df_headers):
            hourlyAverageValues[pos-1], hourlySTDValues[pos-1] = AnalysisUtils().get_hourly_average_value(data_frame = data_frame , 
                                                                                                          column = column,
                                                                                                          min_scale =min_scale,
                                                                                                          unique_days = unique_days,
                                                                                                          device = "cic_card")
            
            new_headers = np.append(new_headers, column)

    if min_scale == "min_scale": period = np.arange(len(unique_minutes)) 
    else:  period = np.arange(len(unique_hours))    
    return new_headers, hourlyAverageValues,hourlySTDValues, day,period

def plot_mopshub_cic_v2_results(modules_name=None, files_name = None, component_name = None,min_scale = None, parameters = None, files_compare = False ): 
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
    
    fig1, ax1 = plt.subplots() 

    for index, (file_name, module_name) in enumerate(zip(files_name, modules_name)):
        file_in_path = root_dir + component_name+"/"
        data_file = file_in_path  +"/data_files/"+file_name+".csv"     
        new_headers, hourlyAverageValues,hourlySTDValues, day,period = load_cic_data(data_file = data_file,
                                                                                     min_scale = min_scale,
                                                                                     component_name = component_name,
                                                                                     module_name = module_name)
        xLabel  = f"Time [{min_scale[:-6]}]" 
        #figName = (str(day)+"_fig_all")
        #plt.figure(figName)
        for col_index, parameter in enumerate(parameters):
            #ax = axes[col_index, col_index]
            #ax.set_title(parameter)  # Set subplot title
            logger.info(f"Plotting {component_name} {modules_name} for data in {file_name}.csv [{min_scale}/{parameter}]")
            if parameter == "coupler":
            # #Plot coupler voltages
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [10])
                selected_headers2 , yValues2 = select_headers_by_indices(new_headers,hourlyAverageValues, [11])
                _ , eyValues = select_headers_by_indices(new_headers,hourlySTDValues, [10])
                _ , eyValues2 = select_headers_by_indices(new_headers,hourlySTDValues, [11])
                yLabel  = ["Current (mA)"]+selected_headers
                yLabel2  = ["Voltage (V)"]+selected_headers2
                fig_coupler, ax_coupler = Plotting().plot_data(xValues = period,
                                                              yValues = yValues,
                                                              eyValues = eyValues,
                                                              xLabel = xLabel,
                                                              yLabel= yLabel,
                                                              min_scale = min_scale,
                                                              modules_name = modules_name,
                                                              title = f'Measured Digital Coupler Paramters {modules_name}',
                                                              posX = 1,
                                                              posY = 1,
                                                              steps = 0.2,
                                                              yValues2 = yValues2,
                                                              yLabel2= yLabel2,
                                                              file_out = f"{data_file[:-4]}_{min_scale[:-6]}"+"_coupler.pdf",
                                                                                              PdfPages = PdfPages)  
                
            elif parameter == "vcan":    
                #Plot U_VCANA & U_VCANB
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [0,12])
                yLabel  = ["Voltage (V)"]+selected_headers
                fig_vcan, ax_vcan = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          min_scale = min_scale,
                                                          modules_name = modules_name,
                                                          title = f'CAN channel voltages {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          steps = 0.5,
                                                          file_out = f"{data_file[:-4]}_{min_scale[:-6]}"+"_vcan.pdf",
                                                          PdfPages = PdfPages)
            
            elif parameter == "current" or parameter == "all": 
                #Plot measured currents
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [1,5,10])
                yLabel  = ["Current (mA)"]+selected_headers
                fig_current, ax_current = Plotting().plot_data(xValues = period,
                                                          yValues = yValues,
                                                          xLabel = xLabel,
                                                          yLabel= yLabel,
                                                          min_scale = min_scale,
                                                          modules_name = modules_name,
                                                          title = f'Measured currents from CIC {modules_name}',
                                                          posX = 1,
                                                          posY = 1,
                                                          steps = 0.04,
                                                          file_out = f"{data_file[:-4]}_{min_scale[:-6]}"+"_current.pdf",
                                                          PdfPages = PdfPages)  
            
            elif parameter == "phy"or parameter == "all":
            #Plot voltages of physical layers
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [2,6])
                yLabel  = ["Voltage (V)"]+selected_headers
            
            
                fig_phy, ax_phy = Plotting().plot_data(xValues = period,
                                                      yValues = yValues,
                                                      xLabel = xLabel,
                                                      yLabel= yLabel,
                                                      min_scale = min_scale,
                                                      modules_name = modules_name,
                                                      title = f'Measured currents from CIC {modules_name}',
                                                      posX = 1,
                                                      posY = 1,
                                                      steps = 0.04,
                                                      file_out = f"{data_file[:-4]}_{min_scale[:-6]}"+"_voltage_phy.pdf",
                                                                                      PdfPages = PdfPages)   
            

            elif parameter == "psu":             
                #Plots CIC PSU current
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [8])
                selected_headers2 , yValues2 = select_headers_by_indices(new_headers,hourlyAverageValues, [9])
                _ , eyValues = select_headers_by_indices(new_headers,hourlySTDValues, [8])
                yLabel  = ["Current (mA)"]+selected_headers
                yLabel2  = ["Voltage (V)"]+selected_headers2
                fig_psu, ax_psu = Plotting().plot_data(xValues = period,
                                                      yValues = yValues,
                                                      yValues2 = yValues2,
                                                      eyValues = eyValues,
                                                      yLabel2= yLabel2,                      
                                                      xLabel = xLabel,
                                                      yLabel= yLabel,
                                                      min_scale = min_scale,
                                                      modules_name = modules_name,
                                                      title = f'Measured CIC PSU Parameters {modules_name}',
                                                      posX = 1,
                                                      posY = 1,
                                                      steps = 0.5,#0.5 before #5 After
                                                      file_out = f"{data_file[:-4]}_{min_scale[:-6]}"+"_current_psu.pdf",
                                                      PdfPages = PdfPages)   
            
            elif parameter == "ntc"or parameter == "all":
            # #Plot NTC voltages
                selected_headers , yValues = select_headers_by_indices(new_headers,hourlyAverageValues, [3,7])
                yLabel  = ["Voltage (V)"]+selected_headers
                fig_ntc, ax_ntc = Plotting().plot_data(xValues = period,
                                                      yValues = yValues,
                                                      xLabel = xLabel,
                                                      yLabel= yLabel,
                                                      min_scale = min_scale,
                                                      modules_name = modules_name,
                                                      title = f'Measured channel NTC voltage {modules_name}',
                                                      posX = 1,
                                                      posY = 1,
                                                      steps = 0.04,
                                                      file_out = f"{data_file[:-4]}_{min_scale[:-6]}"+"_voltage_ntc.pdf",
                                                      PdfPages = PdfPages)   

                if files_compare: 
                    Plotting().plot_data( ax= ax1,
                                          fig = fig1,
                                          xValues = period,
                                          yValues = yValues,
                                          xLabel = xLabel,
                                          yLabel= yLabel,
                                          min_scale = min_scale,
                                          modules_name = modules_name,
                                          title = f'Measured channel NTC voltage {modules_name}',
                                          posX = 1,
                                          posY = 1,
                                          steps = 0.04,
                                          file_out = f"{data_file[:-4]}_{min_scale[:-6]}"+"_voltage_ntc.pdf",
                                          PdfPages = PdfPages)                      
                    #ax1.set_ylabel(yLabel)#("Output Voltage $V_{out}$[V]")
                    #ax1.set_xlabel(xLabel)#("Input Voltage $V_{in}$ [V]")
                    #ile_out = f"{data_file[:-4]}_{min_scale[:-6]}_{parameter}.pdf"
                    #fig.savefig(file_out, bbox_inches='tight')
                  
            else: 
                logger.warning(f"Skip Plotting {parameter} for data in {file_name}.csv [{min_scale}]")
        
        ax1.grid(True)

        ax1.autoscale(enable=True, axis='x', tight=None)
         
    
        #plt.tight_layout()  # Adjust subplot layout
        #plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.4)
        #plt.savefig(root_dir+component_name+"/"+figName+".png")
        #plt.show()
        
# Main function
if __name__ == '__main__':  
    PdfPages = PdfPages(root_dir+'mopshub_cic_v2_tid.pdf') 
    dict_tests_map = AnalysisUtils().open_yaml_file(directory=root_dir , file="tests_map.yaml")
    index_item = [dict_tests_map[i] for i in ["min_tests"] if i in dict_tests_map]
    subindex_items = index_item[0]['cic/TID_results']
    min_tests = { 
        "cic/TID_results":[
                {
                    "after_TID":[
                        {"CIC_TID_Test_03_09_2023_combined":["vcan", "current","phy"]
                         },                   
                        {"CIC_TID_Test_03_09_2023_rst6":["vcan","current","psu", "coupler", "ntc", "phy"]
                         },
                        ]
                }
            ]      
        } 
    
    hr_tests = { 
        "cic/TID_results":[
                {
                    "before_TID": [
                        {
                            "CIC_TID_Test_02_27_2023_00h":["vcan","psu", "coupler"]
                            },
                        ]
                },                   
                {
                    "during_TID": [
                        {
                            "CIC_TID_Test_07_08_09_combined":["vcan","psu", "coupler"]
                            }
                        ]
                } 
            ],
        "cic/neutron_results":[
                {        
                    "before_radiation": [
                        {
                            "CIC_neutron_Test_06_18_2024_combined":["vcan","psu", "coupler"]
                            }                   
                        ],
                    "after_radiation": [
                        {
                            "CIC_neutron_Test_08_04_2024_combined":["vcan","psu", "coupler"]
                            }
                        ],                    
                }
            ],         
            "cic/magnetic_field_results":[
            {        
                # "before_field": [
                #     {
                #         "CIC_magnetic_Test_07_18_2024":["vcan","psu", "coupler"]
                #         }                   
                #     ],
                "during_field": [
                    {
                        "CIC_magnetic_Test_07_19_2024_0":["vcan","psu", "coupler"]
                        },
                    {
                        "CIC_magnetic_Test_07_20_2024_45_combined":["vcan","psu", "coupler"]
                        },
                    {
                        "CIC_magnetic_Test_07_20_2024_90":["vcan","psu", "coupler"]
                        }                    
                    ],        
             }
        ],              
        } 

    modules_name = []  
    tid_min_tests_top = next(iter(min_tests))#get top 
    modules_name = []
    for ic in min_tests[tid_min_tests_top]: modules_name.extend(list(ic.keys()))   
    for ic in min_tests[tid_min_tests_top]:
         for m in ic:            
            for t in ic[m]:
                for p in t:
                    plot_mopshub_cic_v2_results(modules_name=m,
                                                    files_name = m+"/"+list(t.keys())[0],
                                                    parameters =t[p],
                                                    component_name = tid_min_tests_top,
                                                    min_scale = "min_scale")
    
    # AnalysisUtils().combine_csv_files("/home/dcs/git/mopshub-hw-designs/qc_tests/cic/magnetic_field_results/data_files/during_field/CIC_TID_Test_07_19_2024_45.csv",
    #                "/home/dcs/git/mopshub-hw-designs/qc_tests/cic/magnetic_field_results/data_files/during_field/CIC_TID_Test_07_20_2024_45.csv")
    #
    #
    #plot tid Tests
    tid_hr_tests_top = "cic/TID_results"#next(iter(hr_tests))#get top 
    modules_name = []
    for ic in hr_tests[tid_hr_tests_top]: modules_name.extend(list(ic.keys()))   
    for ic in hr_tests[tid_hr_tests_top]:
          for m in ic:            
             for t in ic[m]:
                 #print(list(t.keys())[0])
                 for p in t:    
                     plot_mopshub_cic_v2_results(modules_name=m,
                                                  files_name = m+"/"+list(t.keys())[0],
                                                  parameters =t[p],
                                                  component_name = tid_hr_tests_top,
                                                  min_scale = "h_scale")
                     
    print("---------------------------------------------------------------------------------")
    #plot Magnetic Tests
    magnetic_hr_tests_top = "cic/magnetic_field_results"#next(iter(hr_tests))#get top 
    modules_name = []
    for ic in hr_tests[magnetic_hr_tests_top]: modules_name.extend(list(ic.keys()))   
    for ic in hr_tests[magnetic_hr_tests_top]:
          for m in ic:            
             for t in ic[m]:
                 #print(list(t.keys())[0])
                 for p in t:    
                     plot_mopshub_cic_v2_results(modules_name=m,
                                                  files_name = m+"/"+list(t.keys())[0],
                                                  parameters =t[p],
                                                  component_name = magnetic_hr_tests_top,
                                                  min_scale = "h_scale")
                     

     #
    # # #plot Neutron Tests
    neutron_hr_tests_top = "cic/neutron_results" 
    modules_name = []
    for ic in hr_tests[neutron_hr_tests_top]: modules_name.extend(list(ic.keys()))   
    for ic in hr_tests[neutron_hr_tests_top]:
         for m in ic:            
            for t in ic[m]:
                for p in t:    
                    if m == "full_scan":
                        files_compare = [list(d.keys())[0] for d in ic[m]]
                        print(files_compare)
                        component_name = "cic/neutron_results"
                        file_directory = f"{neutron_hr_tests_top}/{m}/"
                    else:
                        plot_mopshub_cic_v2_results(modules_name=m,
                                                     files_name = m+"/"+list(t.keys())[0],
                                                     parameters =t[p],
                                                     component_name = neutron_hr_tests_top,
                                                     min_scale = "h_scale", 
                                                     files_compare = False )
                                   
    PdfPages.close()
    

