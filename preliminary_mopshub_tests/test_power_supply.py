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
log_call = Logger(log_format=log_format, name="Power Supply", console_loglevel=logging.INFO, logger_file=False)
logger = log_call.setup_main_logger()#

rootdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, rootdir+'/power_card')
root_dir = rootdir+"/"

timeout = 1
time_now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
output_dir = rootdir+"/output_dir/"+time_now

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

def test_power_supply(instrument = None,card_id = None,output1=None,output2=None,voltage = None):
    power_card_outname = f"card_{card_id}"
    power_card_csv_writer, power_card_csv_file = AnalysisUtils().build_data_base(fieldnames=['TimeStamp','elabsed_time',"Usin1(V)","eUsin1(V)","Usin2(V)","eUsin2(V)",
                                                                             "Isin1(A)","eIsin1(A)","Isin2(A)","eIsin2(A)"],
                                                               outputname = power_card_outname, 
                                                               directory = output_dir+"_power_card_tid")        
    monitoringTime = time.time()
    i = 0
    # Register the termination signal handler
    atexit.register(exit_handler)
    try:
        while True:
                i = i+1
                voltage_mean_1, voltage_std_1,current_mean_1, current_std_1 = E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= voltage, current =None,  output=output1)
                voltage_mean_2, voltage_std_2,current_mean_2, current_std_2  = 0.0, 0.0, 0.0, 0.0 #E36xxA_lib.set_power_source_parameters(instrument = instrument,voltage= "2.0",output = output1) 
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
                                     str(current_std_2)))       
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
                     "End of Test"))  
    
        logger.info(f"Data are saved to {output_dir}/{power_card_outname}") 

if __name__ == '__main__':
    #E36xxA_lib.list_available_devices(msg = True, identification_to_check = "E3648A")
    instrument, rm, identification = E36xxA_lib.initialize_power_devices(check = False, resource = 'ASRL/dev/ttyUSB0::INSTR')
    out1,out2 = E36xxA_lib.get_device_outputs(identification = identification)
    #E36xxA_lib.set_power_source_limits(instrument = instrument,max_current = "1.0", output=out1)
    #E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= "0",  current = None, output=out1)
    #E36xxA_lib.set_power_source_parameters(instrument = instrument, voltage= "0", current = None, output=out2)
    #voltage_output,current_output = E36xxA_lib.get_power_measured_parameters(instrument = instrument, output=1,num_samples = 5)
    test_power_supply(instrument = instrument,card_id = "power_supply", output1=out1,output2=out2, voltage = "18.0")
    #arduino_server.close()
    #E36xxA_lib.get_power_measured_parameters(instrument= instrument,output = 1,num_samples = 3 ) 
    #E36xxA_lib.close_power_devices(instrument = instrument, rm = rm)
    