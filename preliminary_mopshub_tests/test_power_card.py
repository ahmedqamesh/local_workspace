########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.08.2023
"""
########################################################

import math
import random # For randint
import sys # For sys.argv and sys.exit
import numpy as np
import time
import os
import binascii
import struct
import serial
import time
import csv
import pyvisa
from datetime import datetime
import atexit
import tests_lib.power_supply_E36xxA_utils as E36xxA_lib
from tests_lib.serial_wrapper_main import SerialServer
from tests_lib.analysis_utils      import AnalysisUtils
from tests_lib.logger_main   import Logger
import logging
log_format = '%(log_color)s[%(levelname)s]  - %(name)s -%(message)s'
log_call = Logger(log_format=log_format, name="Power Card", console_loglevel=logging.INFO, logger_file=False)
logger = log_call.setup_main_logger()#

rootdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, rootdir+'/power_card')
root_dir = rootdir+"/"
test_name = "dcdc_after_neutron"
timeout = 0.5
time_now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
output_dir = rootdir+"/output_dir/"+time_now

def get_arduino_measured_parameters(arduino_server = None, output=None,num_samples = None):    
    return_values = [None,None,None,None ]
    Uout_values = []
    Uiout_values = []
    Iout_values = []
    Uin_values = []
    calculated_values = []       
    s = 0
    while s <num_samples:
        line = arduino_server.read_full_line()
        #print(line)
        # Split the line into individual values based on comma delimiter
        values = line.split(',')
        if len(values) == 3:
            return_values = values + [None] * (3 - len(values))     
            logger.report(f"Sampled {return_values}")  
            if any(value is not None for value in return_values):
                Uout_values.append(float(return_values[0]))
                Uiout_values.append(float(0))
                Iout_values.append(float(return_values[1]))
                Uin_values.append(float(return_values[2]))
                s = s+1
        else:
            continue
        
    Uout_mean, Uout_std = calculate_error(values = Uout_values,unit = "Uout",output = output)
    Uiout_mean, Uiout_std = calculate_error(values = Uiout_values,unit =  "Uiout", output = output)
    Iout_mean, Iout_std = calculate_error(values = Iout_values,unit =  "Iout", output = output)
    Uin_mean, Uin_std = calculate_error(values = Uin_values,unit =  "Uin", output = output)
    calculated_values = [Uout_mean, Uout_std, Uiout_mean,Iout_mean,Iout_std, Uin_mean]
    
    return calculated_values

def calculate_error(values = None, unit = "",output = None):
    mean_value = np.mean(values)
    std_dev = np.std(values)
    logger.report(f"Output {unit}[{output}]: {mean_value:.3f}+/-{std_dev:.3e}")
    return mean_value, std_dev
         
         
def read_adc_data(arduino_server = None):
    return_values = [None,None,None,None,None]
    #for i in np.arange(0,5):
    try:
    #line = arduino_server.readline().strip().decode()
        while True:
            line = arduino_server.read_full_line()
            # Split the line into individual values based on comma delimiter
            values = line.split(',')
            if len(values) == 3:
                return_values = [values[0], 0, values[1],values[2],0] 
                break
            else:
                continue
    except: pass
    time.sleep(timeout)
    logger.info(f"{return_values}")
    return return_values

def exit_handler():
# This function will be called on script termination
    logger.warning("Closing the program.") 
    sys.exit(0)
             
def test_powercard(arduino_server = None, instrument = None,card_id = None,output1=None,output2=None):
    power_card_outname = f"{card_id}_{test_name}"
    logger.info(f"Preparing Test for Card No. {card_id}") 
    power_card_csv_writer, power_card_csv_file = AnalysisUtils().build_data_base(fieldnames=['TimeStamp','elabsed_time',"Usin1(V)","eUsin1(V)","Usin2(V)","eUsin2(V)",
                                                                             "Isin1(A)","eIsin1(A)","Isin2(A)","eIsin2(A)",
                                                                             "Uout1(V)","eUout1(V)","Uout2(V)","eUout2(V)",
                                                                             "Iout1(A)","eIout1(A)","Iout2(A)","eIout2(A)","Uin(V)","Uiout(V)"],
                                                                   outputname = power_card_outname, 
                                                                   directory = output_dir+" power_card_test")              
    monitoringTime = time.time()
    i = 0
    # Register the termination signal handler
    atexit.register(exit_handler)
    try:
        while i<=25:
                i = i+0.5  
                time.sleep(0.5)              
                voltage_mean_1, voltage_std_1,current_mean_1, current_std_1 = E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= str(i), current =None,  output=output2)
                voltage_mean_2, voltage_std_2,current_mean_2, current_std_2  = 0.0, 0.0, 0.0, 0.0 #E36xxA_lib.set_power_source_parameters(instrument = instrument,voltage= "2.0",output = output1) 
                return_values = get_arduino_measured_parameters(arduino_server = arduino_server, output=output2,num_samples = 5)
                #return_values = read_adc_data(arduino_server = arduino_server)
                ts = time.time()
                file_time_now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                elapsedtime = ts - monitoringTime      
                power_card_csv_writer.writerow((str(file_time_now),
                                     str(elapsedtime),
                                     str(voltage_mean_1),
                                     str(voltage_std_1),                                                    
                                     str(voltage_mean_2),
                                     str(voltage_std_2),   
                                     str(current_mean_1),
                                     str(current_std_1),                                                 
                                     str(current_mean_2),
                                     str(current_std_2),                                                    
                                     str(return_values[0]),
                                     str(return_values[1]),                                     
                                     str(0.0),     
                                     str(0.0),                                     
                                     str(return_values[3]), 
                                     str(return_values[4]),                                     
                                     str(0.0),     
                                     str(0.0),  
                                     str(return_values[5]),
                                     str(return_values[2])))             
                power_card_csv_file.flush() # Flush the buffer to update the file
                time.sleep(timeout)
                print(f"--------------------------------------------------------------------")
    except (KeyboardInterrupt):
        #Handle Ctrl+C to gracefully exit the loop
        logger.warning("User interrupted")
        sys.exit(1)      
    finally:
        E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= "0.0", output=output2)
        E36xxA_lib.set_power_source_parameters(instrument = instrument,voltage= "0.0", output=output1) 
        power_card_csv_writer.writerow((str(None),
                     str(None),
                     str(None),
                     str(None),
                     str(None),
                     str(None),
                     str(None),
                     str(None),
                     str(None), 
                     str(None),
                     str(None),
                     str(None),
                     str(None),
                     str(None),
                     str(None), 
                     str(None),
                     str(None),                     
                     str(None),
                     str(None),
                     "End of Test"))   
        logger.info(f"Data are saved to {output_dir}_{test_name}/{power_card_outname}") 
                    
def read_powercard_tid_channels(server = None, instrument = None,card_id = None,output1=None,output2=None,voltage = None):
    power_card_outname = f"{card_id}_power_card_tid"
    power_card_csv_writer, power_card_csv_file = AnalysisUtils().build_data_base(fieldnames=['TimeStamp','elabsed_time',"Usin1(V)","eUsin1(V)","Usin2(V)","eUsin2(V)",
                                                                             "Isin1(A)","eIsin1(A)","Isin2(A)","eIsin2(A)",
                                                                             "Uout1(V)","eUout1(V)","Uout2(V)","eUout2(V)",
                                                                             "Iout1(A)","eIout1(A)","Iout2(A)","eIout2(A)","Uin(V)","Uiout(V)"],
                                                               outputname = power_card_outname, 
                                                               directory = output_dir+"_power_card_tid")        
    monitoringTime = time.time()
    i = 0
    # Register the termination signal handler
    atexit.register(exit_handler)
    try:
        while True:
                i = i+1
                voltage_mean_1, voltage_std_1,current_mean_1, current_std_1 = E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= voltage, current =None,  output=output2)
                voltage_mean_2, voltage_std_2,current_mean_2, current_std_2  = 0.0, 0.0, 0.0, 0.0 #E36xxA_lib.set_power_source_parameters(instrument = instrument,voltage= "2.0",output = output1) 
                return_values = get_arduino_measured_parameters(arduino_server = arduino_server, output=output2,num_samples = 20)
                ts = time.time()
                file_time_now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                elapsedtime = ts - monitoringTime      
                power_card_csv_writer.writerow((str(file_time_now),
                                             str(elapsedtime),
                                             str(voltage_mean_1),
                                             str(voltage_std_1),                                                    
                                             str(voltage_mean_2),
                                             str(voltage_std_2),   
                                             str(current_mean_1),
                                             str(current_std_1),                                                 
                                             str(current_mean_2),
                                             str(current_std_2),                                                    
                                             str(return_values[0]),
                                             str(return_values[1]),                                     
                                             str(0.0),     
                                             str(0.0),                                     
                                             str(return_values[3]), 
                                             str(return_values[4]),                                     
                                             str(0.0),     
                                             str(0.0),  
                                             str(return_values[5]),
                                             str(return_values[2])))       
                power_card_csv_file.flush() # Flush the buffer to update the file
                time.sleep(timeout)
                print(f"--------------------------------------------------------------------")
    except (KeyboardInterrupt):
        #Handle Ctrl+C to gracefully exit the loop
        logger.warning("User interrupted")
        sys.exit(1)      
    finally:
        E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= "0.0", output=output1)
        E36xxA_lib.set_power_source_parameters(instrument = instrument,voltage= "0.0",output = output2) 
        power_card_csv_writer.writerow((str(None),
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None), 
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None),
                                         str(None), 
                                         str(None),
                                         str(None),                     
                                         str(None),
                                         str(None),
                                         "End of Test"))
        logger.info(f"Data are saved to {output_dir}_power_card_tid/{power_card_outname}") 

if __name__ == '__main__':
    arduino_server = SerialServer(baudrate=9600,device = "ttyACM0")
    #arduino_server.list_available_ports(msg = True)
    instrument, rm, identification = E36xxA_lib.initialize_power_devices(check = False, resource = 'ASRL/dev/ttyUSB0::INSTR')
    #time.sleep(0.5)
    out1,out2 = E36xxA_lib.get_device_outputs(identification = identification)
    time.sleep(0.25)
    #E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= "6.0", current = None, output="P6V")
    #E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= "16.0", current = None, output=out2)
    #return_values = get_arduino_measured_parameters(arduino_server = arduino_server, output=out2,num_samples = 10)
    #voltage_output,current_output = E36xxA_lib.get_power_measured_parameters(instrument = instrument, output=1,num_samples = 5)
    test_powercard(arduino_server = arduino_server, instrument = instrument,card_id = "1BH", output1=out1,output2=out2)
    #read_powercard_tid_channels(server = arduino_server, instrument = instrument,card_id = "4_v2_nachtid", output1=out1,output2=out2, voltage = "18.0")
    arduino_server.close()
    #E36xxA_lib.get_power_measured_parameters(instrument= instrument,output = 1,num_samples = 3 ) 
    #E36xxA_lib.close_power_devices(instrument = instrument, rm = rm)
    