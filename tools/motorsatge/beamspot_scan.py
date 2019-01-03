#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#
from basil.dut import Dut
import time
import numpy as np
import tables as tb
import csv
import logging
from tables import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
from matplotlib.backends.backend_pdf import PdfPages
from Tkinter import *
def Restore_intial_positions(Limit=6e6):
    dut = Dut('motorstage_Pyserial.yaml')
    dut.init()
    # Auto-Referencing Option: With standard PI stages
#     dut["ms"]._write_command("FE2", address=1)
#     dut["ms"]._write_command("FE2", address=2)
#     dut["ms"]._write_command("FE2", address=3)
 # Search starts in negative direction 
    dut["ms"]._write_command("FE1,RP", address=3)  #(To start from the extreme left)
    dut["ms"]._write_command("FE1,RP", address=1)  # (To start from the extreme left)
    
def beamspot(size_x=60000, z=3, x_Delay=2, x=5,intialise=False,
         Directory=False, Sourcemeter=False, CurrentLimit=1.000000E-06):
    '''
    Assuming that the cabinet door is the -z
    x : Number of movements to x direction 
    z: Number of movements inside the cabinet
    Size_x: size of the steps in x direction
    '''
    if Sourcemeter:
        dut = Dut('Scanning_pyserial.yaml')
        dut.init()
        dut['ms'].write(":OUTP ON")
        dut['ms'].write("*RST")
        dut['ms'].write(":SOUR:VOLT:RANG 60")
        dut['ms'].write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", dut['ms'].ask("SENS:CURR:PROT?")
        dut['ms'].write(":SOUR:FUNC VOLT")
        dut['ms'].write(':SOUR:VOLT 50')
        val = dut['ms'].ask(":MEAS:CURR?")
        current = val[15:-43]
    else:
        dut = Dut('motorstage_Pyserial.yaml')
        dut.init()
        current = random.randint(1, 101)
        
    def Move(step_z=False,size_x=size_x,current=0.0):
        logging.info('### Shifting z into loop No. %d####'%z)
        if step_z % 2 == 0:
            a,b,c = 0,x,1
            print "Even" , size_x,range(a,b,c)
        else:
           size_x = size_x*-1
           a,b,c = x-1,-1,-1
           print "odd", size_x,range(a,b,c) 
        for step_x in xrange(a,b,c):
            dut["ms"].read_write("MR%d" % (size_x), address=1) # x 50000,100,50 = 4.5 cm
            time.sleep(x_Delay)
            beamspot[step_z,step_x] = float(current)
            plt.imshow(beamspot, aspect='auto', origin='lower', interpolation='gaussian', cmap=plt.get_cmap('tab20c'))
            plt.pause(0.05)
            print beamspot[step_z,step_x],step_x,step_z
        dut["ms"].read_write("MR%d" % (size_x), address=3)  # x# x 50000,100,50 = 4.5 cm 
    plt.show()
    t0 = time.time()
    if intialise:
        dut["ms"]._write_command("FE1,RP", address=3)  # Search starts in negative direction (To start from the extreme left)
        dut["ms"]._write_command("FE1,RP", address=1)  # Search starts in negative direction (To start from the extreme left)
    beamspot = np.zeros(shape=(z, x), dtype=np.float64)
    for step_z in range(z):
        Move(step_z=step_z,current=current)
    with tb.open_file(Directory + "beamspot.h5", "w") as out_file_h5:
        out_file_h5.create_array(out_file_h5.root, 'beamspot', beamspot, "beamspot")  
    print "The beamspot file is saved as%s" %(Directory + "beamspot.h5")
    t1 = time.time()
    print "The time Estimated", t1 - t0


'''
Step1: Restore the intial position with Auto-Referencing Option: With standard PI stages
step2: show GUI to control the motor stage 
'''
Directory = "/home/silab62/git/XrayMachine_Bonn/tools/motorsatge/"
#Restore_intial_positions()
#beamspot(Directory=Directory)


#scan.Plan(Size_x=20000, Steps=442, width=20, Sourcemeter=True, Motor_Delay=2)
#scan.Plan2(Size_x=20000, Steps=150, width=50, Sourcemeter=True, Motor_Delay=2)
