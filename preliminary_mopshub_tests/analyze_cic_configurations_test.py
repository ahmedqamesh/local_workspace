########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.08.2023
"""
########################################################

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
from validators import length
import sys
from datetime import datetime, timedelta
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from tests_lib.plotting   import Plotting
from tests_lib.analysis_utils      import AnalysisUtils
import logging
from matplotlib.dates import DateFormatter
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger("CIC")
rootdir = os.path.dirname(os.path.abspath(__file__))
root_dir = rootdir+"/"
output_dir = rootdir+"/cic/"
from tests_lib.plot_style import *

def load_data(data_file = None):
    data_frame = pd.read_csv(data_file,engine='python')
    logger.info(f"Loading  Data")    
    # logger.info the headers
    file_dir = os.path.dirname(os.path.abspath(data_file))
    df_headers = data_frame.columns.tolist()
    data_frame = AnalysisUtils().check_last_row(data_frame = data_frame, column = df_headers[-1])
    return data_frame, df_headers,file_dir+"/" 


data_seu = {
    "Unflipped":  {0x03:1.9, 0x0F:2.0, 0x33:2.4, 0x3F:2.6, 0xC3:2.8, 0xCF:3.5, 0xF3:4.2, 0xFF:4.6},
    "flipbit_0" : {0x02:0  , 0x0E:0  , 0x32:0  , 0x3E:0  , 0xC2:0  , 0xCE:0  , 0xF2:0  , 0xFE:0},
    "flipbit_1" : {0x01:0  , 0x0D:0  , 0x31:0  , 0x3D:0  , 0xC1:0  , 0xCD:0  , 0xF1:0  , 0xFD:0},    
    "flipbit_2" : {0x07:1.9, 0x0B:1.9, 0x37:2.4, 0x3B:2.4, 0xC7:2.8, 0xCB:2.8, 0xF7:4.2, 0xFB:4.2},   
    "flipbit_3" : {0x0B:1.9, 0x07:1.9, 0x3B:2.4, 0x37:2.4, 0xCB:2.8, 0xC7:2.8, 0xFB:4.2, 0xF7:4.2},   
    "flipbit_4" : {0x13:1.9, 0x1F:2.0, 0x23:1.9, 0x2F:2.0, 0xD3:2.8, 0xDF:3.5, 0xE3:2.8, 0xEF:3.5},   
    "flipbit_5" : {0x23:1.9, 0x2F:2.0, 0x13:1.9, 0x1F:2.0, 0xE3:2.8, 0xEF:3.5, 0xD3:2.8, 0xDF:3.5},
    "flipbit_6" : {0x43:1.9, 0x4F:2.0, 0x73:2.4, 0x7F:2.6, 0x83:1.9, 0x8F:2.0, 0xB3:2.4, 0xBF:2.6},
    "flipbit_7" : {0x83:1.9, 0x8F:2.0, 0xB3:2.4, 0xBF:2.6, 0x43:1.9, 0x4F:2.0, 0x73:2.4, 0x7F:2.6},
    }


data_all = {
    "all":  {0x03:1.9,0x13:1.9,0x23:1.9,0x33:2.4,0x43:1.9,0x53:1.9,0x63:1.9,0x73:2.4,0x83:1.9,0x93:1.9,0xA3:1.9,0xB3:2.4,0xC3:2.8,0xD3:2.8,0xE3:2.8,0xF3:4.25,    
             0x07:1.9,0x17:1.9,0x27:1.9,0x37:2.4,0x47:1.9,0x57:1.9,0x67:1.9,0x77:2.4,0x87:1.9,0x97:1.9,0xA7:1.9,0xB7:2.4,0xC7:2.8,0xD7:2.8,0xE7:2.8,0xF7:4.2,
             0x0B:1.9,0x1B:1.9,0x2B:1.9,0x3B:2.4,0x4B:1.9,0x5B:1.9,0x6B:1.9,0x7B:2.4,0x8B:1.9,0x9B:1.9,0xAB:1.9,0xBB:2.4,0xCB:2.8,0xDB:2.8,0xEB:2.8,0xFB:4.2,
             0x0F:2.0,0x1F:2.0,0x2F:2.0,0x3F:2.6,0x4F:2.0,0x5F:2.0,0x6F:2.0,0x7F:2.6,0x8F:2.0,0x9F:2.0,0xAF:2.0,0xBF:2.6,0xCF:3.5,0xDF:3.5,0xEF:3.5,0xFF:4.6}
    }
    
# Main function
if __name__ == '__main__':
    # get program arguments
    PdfPages = PdfPages(root_dir+'mopshub_cic_configurations.pdf')
    files = ["card_0_v4/card_0_v4.csv", "card_1_v4/card_1_v4.csv"]
    
    for file in files: 
        data_frame, _,file_dir = load_data(data_file = f"{root_dir}cic/powering_tests/{file}")
        Plotting().mopshub_cic_v4_configurations(data= data_frame, output_dir = file_dir, PdfPages = PdfPages)
        Plotting().mopshub_cic_v4_resistance(data= data_frame, output_dir = file_dir, PdfPages = PdfPages)
        Plotting().mopshub_cic_v4_configurations_seu(data= data_frame,data_seu= data_seu, output_dir = file_dir, PdfPages = PdfPages)
        Plotting().mopshub_cic_v4_configuations_all(data= data_frame,data_all= data_all, output_dir = file_dir, PdfPages = PdfPages)
    PdfPages.close()

