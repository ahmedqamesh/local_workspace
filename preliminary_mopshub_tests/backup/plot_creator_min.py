import datetime 
import sys
import time
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def getDay(TimeStamps): 
    pos = 0
    day = ""
    while TimeStamps[0][pos] != chr(32):
        day += TimeStamps[0][pos]
        pos += 1
    return day

def getHours(TimeStamps):
    hour = 0
    hours = [[""]*1 for i in range(len(TimeStamps))]
    print(str(len(TimeStamps)))
    for i in TimeStamps: 
        hours[hour] = i[14] + i[15] #14+15 for min and 11+12 for hours
        hour += 1
        
    return hours

def getHourlyAverageValue(hours, data):
    dataSum = [np.zeros(0) for i in range(60)] #24 if hours and 60 if min 
    
    pos = 0
    for hour in hours:
        try:
            dataSum[int(hour)] = np.append(dataSum[int(hour)],float(data[pos]))
            pos += 1
        except: 
            print("No real Number")
    
    hourlyAverageValues = [[""]*1 for i in range(len(dataSum))]
    for hour in range(len(dataSum)): 
        if dataSum[hour].any() >0:
            hourlyAverageValues[hour] = np.average(dataSum[hour])
        else: 
            hourlyAverageValues[hour] = None
    return hourlyAverageValues
        
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
    plt.xticks(np.arange(0,62,2))
    plt.legend()
    plt.xlabel(xLabel)
    plt.grid(True)
    plt.ylabel(yLabel[0])
    
columns=["TimeStamp", "U_CIC_VCANA", "I_CIC_VCANA", "V_MOPSA", "V_NTCA", "U_CIC_VCANB", "I_CIC_VCANB", "V_MOPSB", 
         "V_NTCB", "I_CIC_PSU", "U_CIC_PSU",  "I_DCoupl",  "U_DCoupl",  "U_VCANA",  "U_VCANB", "Can_Working", "ERROR"]
frames = [pd.DataFrame(columns=columns) for i in range(len(sys.argv))]

#argTest = ["","CIC_TID_Test_03_09_2023_rst6.csv"]
argTest = ["","/home/dcs/git/mopshub-hw-designs/tests/cic/Irradiation_campaign/data_files/nachTID/CIC_TID_Test_03_09_2023_rst6.csv"]
for number, file in enumerate(argTest):
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
day = getDay(df.TimeStamp)
hours = getHours(df.TimeStamp)
hourlyAverageValues = [0 for i in range(len(columns))]
for pos,column in enumerate(columns): 
    if pos > 0 and pos < len(columns)-2:
        hourlyAverageValues[pos-1] = getHourlyAverageValue(hours,df[column])

period = np.arange(60) # 24 for hours and 60 for min 
figName = (str(day)+ "_" + str(df.TimeStamp[0][11:13]) + "h_fig1")
plt.figure(figName,figsize=(10,8))

#Plot U_VCANA & U_VCANB
plot(period,[hourlyAverageValues[0],hourlyAverageValues[12],hourlyAverageValues[4],hourlyAverageValues[13]],"Time (min)",
     ["Voltage (V)", "U_CIC_VCANA","U_VCANA","U_CIC_VCANB", "U_VCANB"],'CAN channel voltages',2,1,0.04)

#Plot measured currents
plot(period,[hourlyAverageValues[1], hourlyAverageValues[5],hourlyAverageValues[10]],
     "Time (min)",["Current (mA)","I_CIC_VCANA", "I_CIC_VCANB","I_DCoupl"],
     'Measured currents from CIC',2,2,0.5)

plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.4)
plt.savefig(figName+".png")

figName = (str(day)+ "_" + str(df.TimeStamp[0][11:13]) + "h_fig2")
plt.figure(figName,figsize=(10,8.5))
#Plot voltages of physical layers
plot(period,[hourlyAverageValues[2], hourlyAverageValues[6]],
     "Time (min)",["Voltage (V)","V_MOPSA", "V_MOPSB"],
     'Measured voltages of physical layers',3,1,0.04)

#Plots CIC PSU current
plot(period,[hourlyAverageValues[8]],
     "Time (min)",["Current (mA)","I_CIC_PSU"],
     'Measured CIC PSU current',3,2,0.2)

#Plot NTC voltages
plot(period,[hourlyAverageValues[3],hourlyAverageValues[7]],
     "Time (min)",["Voltage (V)","V_NTCA", "V_NTCB"],
     'Measured channel NTC voltage',3,3,0.04)

plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.4)
plt.savefig(figName+".png")
plt.show()