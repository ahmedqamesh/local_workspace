#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#

''' Example how to use different laboratory devices (Source, pulsers, etc.) that understand SCPI.
    The language (SCPI) is independent of the interface (TCP, RS232, GPIB, USB, etc.). The interfaces
    can be choosen by an appropriate transportation layer (TL). This can be a VISA TL and
    a Serial TL at the moment. VISA TL is recommendet since it gives you access to almost
    all laboratory devices (> 90%) over TCP, RS232, USB, GPIB (Windows only so far).
    '''
from basil.dut import Dut
# Talk to a Keithley device via serial port using pySerial
dut = Dut('keithley2400_pyserial.yaml')
dut.init()
dut['Sourcemeter'].write(":OUTP ON")
dut['Sourcemeter'].write("*RST")
dut['Sourcemeter'].write(":SOUR:VOLT:RANG 60")
#dut['Sourcemeter'].IV_Test(CurrentLimit=1.0e-06,start_V=2,step_V=-1,end_V=-20,Stat_Delay=10,Itterations=3,Plot=True,chip_num=2)

#dut['Sourcemeter'].Plotting_IVcurve(start_V=0,step_V=-1,end_V=-20,
#                                    F='/home/silab62/MasterWork/IV_table.csv')
#dut['Sourcemeter'].Plotting_IVcurve_Stat(Directory='/home/silab62/MasterWork/',h5=True)
#dut['Sourcemeter'].write(":OUTP OFF")