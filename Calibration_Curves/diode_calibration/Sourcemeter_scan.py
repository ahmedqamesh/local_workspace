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
Directory = "/home/silab62/git/XrayMachine_Bonn/tests/diode_calibration/"
dut = Dut('keithley2400_pyserial.yaml')
dut.init()
dut['sm'].write(":OUTP ON")
dut['sm'].write("*RST")
dut['sm'].write(":SOUR:VOLT:RANG 60")
dut['sm'].IV_test(Directory=Directory,CurrentLimit=1.0e-06,start_V=0,step_V=2,end_V=50,Stat_Delay=3,Itterations=5,Plot=True,diodes=["C"])
#dut['sm'].Plotting_IV_test(Directory=Directory,diodes=["A"])
dut['sm'].write(":OUTP OFF")