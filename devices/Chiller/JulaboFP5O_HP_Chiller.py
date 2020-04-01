#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# ------------------------------------------------------------
from basil.dut import Dut
# Sensirion sensor readout
dut = Dut('JulaboFP50_HP.yaml')
dut.init()
dut["JulaboFP50"].Switch_mode(Switch=0) # switch =1 is on / switch =0 is off
#dut["JulaboFP50"].Run_mode(Run=1)
#dut["JulaboFP50"].Set_Settings(Set=0, value=25) #Set= 0 for T1 / Set= 1 for T2
