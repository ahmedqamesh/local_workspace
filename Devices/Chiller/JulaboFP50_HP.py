#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# ------------------------------------------------------------
#
from basil.HL.RegisterHardwareLayer import HardwareLayer


class JulaboFP50(HardwareLayer):
    '''Driver for  JolaboFP50 Controller.
    A protocoll via RS 232 serial port is used with 4800 baud rate. 
    '''
    def __init__(self, intf, conf):
        super(JulaboFP50, self).__init__(intf, conf)

    def write(self, value):
        msg = value + '\r'  # msg has CR at the end
        self._intf.write(str(msg))

    def read(self, command=None):
        answer = self._intf._readline()
        return answer

    def Switch_mode(self, Switch=2):
        # Circulator in Stop/Start condition:
        if Switch == 1:
            self.write("out_mode_05 1")
            self.read()

        if Switch == 0:
            self.write("out_mode_05 0")
            self.read()

    def Set_Settings(self, Set=None, value=None):
        if Set == 0:  # Set to T1
            self.write('out_sp_00 %d' % value)
        if Set == 1:  # Set to T2
            self.write('out_sp_01 %d' % value)

    def Run_mode(self, Run=0):
        # Selected working temperature:
        if Run == 1:
            self.write("out_mode_01 0")  # Select T1
        if Run == 2:
            self.write("out_mode_01 1")  # Select T2
