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
    dut["ms"]._write_command("FE0,RP", address=2)  # (To start from the extreme in)
    
def beamspot(size_x=1, z=20, x_Delay=5, x=20,size_z=1,
         Directory=False, Sourcemeter=True, CurrentLimit=1.000000E-06):
    '''
    Assuming that the cabinet door is the -z
    1 mm is equivalent to 56.88888 step
    x : Number of movements to x direction 
    z: Number of movements inside the cabinet
    Size_x: size of the step in  mm x direction
    Size_z: size of the step in  mm z direction
    '''
    #def beamspot(size_x=5*57000, z=25, x_Delay=5*3, x=25,size_z=5*57000 51 scan
    size_x = size_x*57000
    size_z=size_z*57000
    if Sourcemeter:
        dut = Dut('Scanning_pyserial.yaml')
        dut.init()
        dut['sm'].write(":OUTP ON")
        #dut['sm'].write("*RST")
        #dut['sm'].write(":SOUR:VOLT:RANG 60")
        #dut['sm'].write('SENS:CURR:PROT ' + str(CurrentLimit))
        #print "The Protection Current limit is", dut['sm'].ask("SENS:CURR:PROT?")
        dut['sm'].write(":SOUR:FUNC VOLT")
        dut['sm'].write(':SOUR:VOLT 50')
    else:
        dut = Dut('motorstage_Pyserial.yaml')
        dut.init()
        
    def Move(step_z=False,size_x=size_x,size_z=size_z):
        if step_z % 2 == 0:
            a,b,c = 0,x,1
            print "Even" , size_x,range(a,b,c)
        else:
           size_x = size_x*-1
           a,b,c = x-1,-1,-1
           print "odd", size_x,range(a,b,c) 
        
        first_point = True
        for step_x in xrange(a,b,c):
            if not first_point:
                dut["ms"].read_write("MR%d" % (size_x), address=3) # x 50000,100,50 = 4.5 cm left/right
            first_point = False
            time.sleep(x_Delay)
            if Sourcemeter:
                val = dut['sm'].ask(":MEAS:CURR?")
                current = val[15:-43]
            else:
                current = random.randint(1, 101)
            beamspot[step_z,step_x] = float(current)
            plt.imshow(beamspot, aspect='auto', origin='upper',  cmap=plt.get_cmap('tab20c'))
            plt.pause(0.05)
            print beamspot[step_z,step_x],step_x,step_z
        dut["ms"].read_write("MR%d" % (-size_z), address=2)  # x# x 50000,100,50 = 4.5 cm in/out
        time.sleep(2*x_Delay)
    t0 = time.time()
    beamspot = np.zeros(shape=(z, x), dtype=np.float64)
    for step_z in range(z):
        Move(step_z=step_z)
    plt.show()
    file = Directory + "beamspot_3cm_collimator.h5"
    with tb.open_file(file, "w") as out_file_h5:
        out_file_h5.create_array(out_file_h5.root, 'beamspot', beamspot, "beamspot")  
    print "The beamspot file is saved as%s" %(file)
    t1 = time.time()
    print "The time Estimated", t1 - t0
'''
Step1: Restore the intial position with Auto-Referencing Option: With standard PI stages
step2: show GUI to control the motor stage 
'''
Directory = "/home/silab62/git/XrayMachine_Bonn/tools/motorsatge/"
#Restore_intial_positions()
beamspot(Directory=Directory)
