import datetime 
import sys
import time
import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
from tests_lib.analysis_utils      import AnalysisUtils

rootdir = os.path.dirname(os.path.abspath(__file__))
root_dir = rootdir + "/"
output_dir = "/data_files/"

def plot(xValues, yValues, xLabel, yLabel, title, posX, posY,steps):
    yMin = [0 for i in range(len(yValues))]
    yMax = [0 for i in range(len(yValues))]
    plt.subplot(posX, 1, posY)
    plt.title(title)
    for number, value in enumerate(yValues):
        yMin[number] = min((y for y in value if y is not None),key=lambda x:float(x))
        yMax[number] = max((y for y in value if y is not None),key=lambda x:float(x))
        plt.plot(xValues,value,'.-', label = yLabel[number+1])
    plt.yticks(np.arange(min(yMin)-0.05, max(yMax)+0.05,steps))
    plt.xticks(xValues)
    plt.legend()
    plt.xlabel(xLabel)
    plt.grid(True)
    plt.ylabel(yLabel[0])
 
  # Main function
if __name__ == '__main__':  
    columns=["TimeStamp", "U_CIC_VCANA", "I_CIC_VCANA", "V_MOPSA", "V_NTCA", "U_CIC_VCANB", "I_CIC_VCANB", "V_MOPSB", 
             "V_NTCB", "I_CIC_PSU", "U_CIC_PSU",  "I_DCoupl",  "U_DCoupl",  "U_VCANA",  "U_VCANB", "Can_Working", "ERROR"]
    frames = [pd.DataFrame(columns=columns) for i in range(len(sys.argv))]
    
    argTest = ["","/home/dcs/git/mopshub-hw-designs/tests/cic/Irradiation_campaign/data_files/nachTID/CIC_TID_Test_03_09_2023_rst6.csv"]
    for number, file in enumerate(argTest):#sys.argv):
        if number >0:
            print("This is the " +str(number-1)+ " data Frame:")
            frames[number-1] = pd.read_csv(str(file), usecols = columns)
            print(frames[number-1])
            
    for number, frame in enumerate(frames):
        if number == 0: 
            df = frame
        else: 
           df = pd.concat([df,frame], ignore_index=True, sort=False)
    
    print("This is the whole frame:",df)
    day = AnalysisUtils().getDay(df.TimeStamp)
    hours = AnalysisUtils().getHours(df.TimeStamp)
    hourlyAverageValues = [0 for i in range(len(columns))]
    for pos,column in enumerate(columns): 
        if pos > 0 and pos < len(columns)-2:
            hourlyAverageValues[pos-1] = AnalysisUtils().getHourlyAverageValue(hours,df[column])
    
    period = np.arange(24) # 24 for hours and 60 for min 
    figName = (str(day)+"_fig1")
    plt.figure(figName,figsize=(10,8))
    
    #Plot U_VCANA & U_VCANB
    plot(period,[hourlyAverageValues[0],hourlyAverageValues[12],hourlyAverageValues[4],hourlyAverageValues[13]],"Time (h)",
         ["Voltage (V)", "U_CIC_VCANA","U_VCANA","U_CIC_VCANB", "U_VCANB"],'CAN channel voltages',2,1,0.04)
    
    #Plot measured currents
    plot(period,[hourlyAverageValues[1], hourlyAverageValues[5],hourlyAverageValues[10]],
         "Time (h)",["Current (mA)","I_CIC_VCANA", "I_CIC_VCANB","I_DCoupl"],
         'Measured currents from CIC',2,2,0.5)
    
    plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.4)
    plt.savefig(figName+".png")
    
    figName = (str(day)+"_fig2")
    plt.figure(figName,figsize=(10,8.5))
    #Plot voltages of physical layers
    plot(period,[hourlyAverageValues[2], hourlyAverageValues[6]],
         "Time (h)",["Voltage (V)","V_MOPSA", "V_MOPSB"],
         'Measured voltages of physical layers',3,1,0.04)
    
    #Plots CIC PSU current
    plot(period,[hourlyAverageValues[8]],
         "Time (h)",["Current (mA)","I_CIC_PSU"],
         'Measured CIC PSU current',3,2,0.1)
    
    #Plot NTC voltages
    plot(period,[hourlyAverageValues[3],hourlyAverageValues[7]],
         "Time (h)",["Voltage (V)","V_NTCA", "V_NTCB"],
         'Measured channel NTC voltage',3,3,0.04)
    
    plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.4)
    plt.savefig(figName+".png")
    plt.show()