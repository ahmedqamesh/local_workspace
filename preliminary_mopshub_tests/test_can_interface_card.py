########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Felix Nitz (University of Wuppertal)
    email: fnitz@uni-wuppertal.de  
    Date: 29.01.2023
"""
########################################################

import serial
import datetime 
import sys
import time
import pandas as pd
import os
from tests_lib.serial_wrapper_main import SerialServer
class Logger(): 
    def __init__(self):
        self.fileNameDate = str(datetime.datetime.now().strftime("%m_%d_%Y"))
        self.setFileName(self.fileNameDate)

    def logData(self,channelA, channelB, arduinoAdc, canWorkingFlag, timeStamp,errorCode,headerState): 
        df = pd.DataFrame(
        {                
            "U-CIC-VCANA (V)": round(channelA[0],4),
            "I-CIC-VCANA (mA)": round(channelA[1],4),
            "V-MOPSA (V)": round(channelA[2],4),
            "V-NTCA (V)": round(channelA[3],4),
            "U-CIC-VCANB (V)": round(channelB[0],4),
            "I-CIC-VCANB (mA)": round(channelB[1],4),
            "V-MOPSB (V)": round(channelB[2],4),
            "V-NTCB (V)": round(channelB[3],4),
            "I-CIC_PSU (mA)": round(arduinoAdc[0],4),
            "U-CIC_PSU (V)": round(arduinoAdc[1],4),
            "I-DCoupl (mA)": round(arduinoAdc[2],4),
            "U-DCoupl (V)": round(arduinoAdc[3],4),
            "U-VCANA (V)": round(arduinoAdc[4],4),
            "U-VCANB (V)": round(arduinoAdc[5],4),
            "Can-Working": canWorkingFlag,
            "ERROR": errorCode,
        }
        ,index=[timeStamp]
        )
        df.to_csv(os.path.join(self.__location__, self.fileName),mode='a', index=True, header=headerState)
    def setFileName(self,date):
        self.fileNameDate = date
        self.fileName = "CIC_TID_Test_"  + self.fileNameDate + ".csv"
        self.__location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
        try:
            file = open(os.path.join(self.__location__,self.fileName),"x")
            file.close()
        except Exception as exception:
            print("file already exists:\n Save it somewhere else and restart the programm")
            sys.exit(0)
        
class Controller():     
    def __init__(self):
        
        try:
            #self.ser = serial.Serial(sys.argv[1],9600, timeout=1) 
            self.ser = SerialServer(baudrate=9600,device = "ttyACM0")
            if(   self.ser.isOpen() == False):
                    self.ser.open()
        except Exception as exception:
            print("Error Arduino not found")
            sys.exit(0)
        
        self.L = Logger()
        self.rebootFlag = False
        self.initialized = False
        self.index = 0
        self.checkFrequency = 300 #Time in seconds 
        self.rebootTime = "%d" #Power cycles CIC card every  %H for hour or %d for day or %M for minute
        self.channelA = ["" for i in range(4)]
        self.channelB =  ["" for i in range(4)]
        self.arduinoAdcValues = ["" for i in range(6)]
        self.arduinoAdcDec = ["" for i in range(6)]
        self.adcValuesA = ["" for i in range(4)]
        self.adcValuesB =  ["" for i in range(4)]
        self.canDutyCycle = ""
        self.canWorkingFlag = False
        self.errorMessage = ""
        self.main()
        

    def main(self):
        time.sleep(2)
        oldLog = 0
        self.ser.write(bytes([1]))
        time.sleep(4)
        timeStamp = datetime.datetime.now()
        beat = time.time()
        self.initTime = timeStamp.strftime(self.rebootTime)
        
        while(1):
            self.checkForHeartBeat(beat) # must be implemented 
            
            self.checkForRebootTask()
             
            if self.readNewLog(oldLog):
                oldLog = self.log
                beat = time.time()
                timeStamp = datetime.datetime.now()
                
                print("TimeStamp: " + str(timeStamp))
                
                #Get ADC values of channel A 
                print("U-CIC-VCANA: " + self.getAdcValue(1,0)) 
                print("I-CIC-VCANA: " + self.getAdcValue(1,1))
                print("V-MOPSA: " + self.getAdcValue(1,2)) 
                print("V-NTCA : " + self.getAdcValue(1,3))
                
                #Get ADC values of channel B
                print("U-CIC-VCANB: " + self.getAdcValue(2,0)) 
                print("I-CIC-VCANB: " + self.getAdcValue(2,1))
                print("V-MOPSB: " + self.getAdcValue(2,2)) 
                print("V-NTCB : " + self.getAdcValue(2,3))
                
                #Get Arduino ADC values 
                self.getArduinoAdcValues(0)
                self.getArduinoAdcValues(1)
                self.getArduinoAdcValues(2)
                self.getArduinoAdcValues(3)
                self.getArduinoAdcValues(4)
                self.getArduinoAdcValues(5)
                
                #CheckCanInterface
                self.checkCanDutyCycle()
                
                if not self.initialized: 
                    self.initialized = True
                    self.L.logData(self.adcValuesA, self.adcValuesB, self.arduinoAdcValues, self.canWorkingFlag, timeStamp,"None", True)
                else: 
    
                    self.L.logData(self.adcValuesA, self.adcValuesB, self.arduinoAdcValues, self.canWorkingFlag, timeStamp,"None", False)
            
    def checkCanDutyCycle(self):
        if 0.0 < float(self.canDutyCycle) < 1.0:
            self.canWorkingFlag = True
        else: 
            self.canWorkingFlag = False
            self.rebootFlag = True
            self.errorMessage = "Failed to find CAN duty cycle"
        print("CAN-Duty-Cycle: " + self.canDutyCycle + "\n")
         
    def checkForHeartBeat(self, beat):
        lastBeat = time.time() - beat
        if lastBeat > self.checkFrequency: 
            self.rebootFlag = True
            self.errorMessage = "Failed to find heartbeat"
        
        
    def readNewLog(self, oldLog):
        self.channelA = ["" for i in range(4)]
        self.channelB =  ["" for i in range(4)]
        self.arduinoAdcDec = ["" for i in range(6)]
        self.canDutyCycle = ""
        
        self.log = self.ser.readline(); 
        if len(self.log) >0 and self.log != oldLog: 
            pos = 0
            for channelPos in range(0,4):
                while chr(self.log[pos]) != ";":
                    self.channelA[channelPos] += chr(self.log[pos])
                    pos +=1
                pos +=1
                
            for channelPos in range(0,4):
                while chr(self.log[pos]) != ";":
                    self.channelB[channelPos] += chr(self.log[pos])
                    pos +=1
                pos +=1
            
            for channelPos in range(0,6):
                while chr(self.log[pos]) != ";" :
                    self.arduinoAdcDec[channelPos] += chr(self.log[pos])
                    pos +=1
                pos +=1
                
            while chr(self.log[pos]) != ";" and chr(self.log[pos]) != "\n":
                self.canDutyCycle += chr(self.log[pos])
                pos+=1
            
            return True
        
        return False
    
    def getArduinoAdcValues(self, port):
        if port == 0: 
            self.arduinoAdcValues[port] = (int(self.arduinoAdcDec[port])/1023.0)*1100.0
            print("I-CIC_PSU: "+ str(round(self.arduinoAdcValues[port],4)) + " mA")
        elif port == 1: 
            self.arduinoAdcValues[port] = (int(self.arduinoAdcDec[port])/1023.0)*1.1*20
            print("U-CIC_PSU: "+ str(round(self.arduinoAdcValues[port],4)) + " V")
        elif port == 2: 
            self.arduinoAdcValues[port] = (int(self.arduinoAdcDec[port])/1023.0)*1100.0
            print("I-DCoupl: "+ str(round(self.arduinoAdcValues[port],4)) + " mA")
        elif port == 3: 
            self.arduinoAdcValues[port] = (int(self.arduinoAdcDec[port])/1023.0)*1.1*10
            print("U-DCoupl: "+ str(round(self.arduinoAdcValues[port],4)) + " V")
        elif port == 4: 
            self.arduinoAdcValues[port] = (int(self.arduinoAdcDec[port])/1023.0)*1.1*4
            print("U-VCANA: "+ str(round(self.arduinoAdcValues[port],4)) + " V")
        elif port == 5: 
            self.arduinoAdcValues[port] = (int(self.arduinoAdcDec[port])/1023.0)*1.1*4
            print("U-VCANB: "+ str(round(self.arduinoAdcValues[port],4)) + " V")
    
    def getAdcValue(self, channel, port):
        if channel == 1: 
            adcValue = self.channelA[port]
        else: 
            adcValue = self.channelB[port]
            
        adcVoltage = int(adcValue)/65535
        adcVoltage = adcVoltage * 2.5 
    
        if channel == 1: 
            if port == 1: 
                currentMa = 1000 * adcVoltage 
                self.adcValuesA[1] = currentMa
                return str(round(currentMa,4)) + " mA"
            else: 
                self.adcValuesA[port] = adcVoltage
                return str(round(adcVoltage,4)) + " V"
        else: 
            if port == 1: 
                currentMa = 1000 * adcVoltage 
                self.adcValuesB[1] = currentMa
                return str(round(currentMa,4)) + " mA"
            else: 
                self.adcValuesB[port] = adcVoltage
                return str(round(adcVoltage,4)) + " V"
                
    def powerCycle(self): 
        self.ser.write(bytes([2]))
        time.sleep(2)
        self.ser.write(bytes([1]))
    
    def checkForRebootTask(self):
        now = datetime.datetime.now()
        
        if now.strftime(self.rebootTime)>self.initTime:
            self.initTime = now.strftime(self.rebootTime)
            self.L.logData(self.adcValuesA, self.adcValuesB, self.arduinoAdcValues, self.canWorkingFlag, now,"Reboot time reached",False)
            self.L.setFileName(datetime.datetime.now().strftime("%m_%d_%Y"))
            self.powerCycle()
            self.initialized = False
            self.index = 0
            
        if self.rebootFlag: 
            self.rebootFlag = not self.rebootFlag
            self.index +=1
            self.L.logData(self.adcValuesA, self.adcValuesB, self.arduinoAdcValues, self.canWorkingFlag, now, self.errorMessage,False)
            self.L.setFileName(datetime.datetime.now().strftime("%m_%d_%Y")+"_rst"+str(self.index))
            self.initialized = False
            self.powerCycle()
            
                
Controller()