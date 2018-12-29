#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
from basil.dut import Dut
from Tkinter import *
import tkMessageBox
import time
from tkFont import Font
dut = Dut('XRay_Project_pyserial_Tkinter.yaml')
dut.init()
t0 = time.time()
root = Tk()
root.title("X Ray Project")
root.geometry("600x600")
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=False, activeforeground='blue', relief=RAISED)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Save", command=lambda: dut["MotorStage"].print_value())
filemenu.add_separator()
filemenu.add_command(label="Exit", command=lambda: root.quit())

editmenu = Menu(menubar, tearoff=0, activeforeground='blue', relief=RAISED)
menubar.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Copy", command=lambda: dut["MotorStage"].print_value())
editmenu.add_command(label="Cut", command=lambda: dut["MotorStage"].print_value())

Settingsmenu = Menu(menubar, tearoff=0, activeforeground='blue', relief=RAISED)
menubar.add_cascade(label="Settings", menu=Settingsmenu)
subSettingsmenu = Menu(Settingsmenu, tearoff=False, activeforeground='blue', relief=RAISED)
Settingsmenu.add_cascade(label="Controller settings", menu=subSettingsmenu)
subSettingsmenu.add_command(label="Current Motor Status", command=lambda: dut["JulaboFP50"].Motor_mode())
subSettingsmenu.add_command(label="Set Home Position", command=lambda: dut["MotorStage"].PositionSettings(Home=1))
subSettingsmenu.add_command(label="Motor settings", command=lambda: dut["MotorStage"].MotorSettings())
subSettingsmenu.add_command(label="Position settings", command=lambda: dut["MotorStage"].PositionSettings(Set=1))


subSettingsmenu = Menu(Settingsmenu, tearoff=False, activeforeground='blue', relief=RAISED)
Settingsmenu.add_cascade(label="Chiller settings", menu=subSettingsmenu)
subSettingsmenu.add_command(label="Current Temprature Status", command=lambda: dut["JulaboFP50"].Chiller_mode(Temp=1))
subSettingsmenu.add_command(label="Current Power Status", command=lambda: dut["JulaboFP50"].Chiller_mode(Power=1))
subSettingsmenu.add_command(label="Set Temprature Settings", command=lambda: dut["JulaboFP50"].TempratureSettings())
subSettingsmenu.add_command(label="Set Temprature Warning Limits", command=lambda: dut["JulaboFP50"].TempratureLimits())
subSettingsmenu.add_command(label="Set Power Warning Limits", command=lambda: dut["JulaboFP50"].powerLimits())

Helpmenu = Menu(menubar, tearoff=0, activeforeground='blue', relief=RAISED)
menubar.add_cascade(label="Help", menu=Helpmenu)
Helpmenu.add_command(label="Controller Help", command=lambda: dut["MotorStage"].print_value())
Helpmenu.add_command(label="Sensor Help", command=lambda: dut["MotorStage"].print_value())
root.config(menu=menubar)

Reset_button3 = Button(root, padx=4, bd=1, fg="Red", font=Font(family='times', size=9),
                       text="Reset", command=lambda: dut["MotorStage"]._write_command("MA0", address=3)).place(x=245, y=240)

# Part for Chillar
lblInfo = Label(root, padx=8, font=Font(family='times', size=11, weight='bold'),
                text="===============Julabo Chiller Settings===============", fg="Black", anchor='w').place(x=12, y=300)

ON_Chiller = Button(root, fg="black", width=3,
                    text="ON", font=Font(family='times', size=11), background="green",
                    command=lambda: dut["JulaboFP50"].Run_mode(Switch=1)).place(x=10, y=340)
OFF_Chiller = Button(root, fg="black", width=3,
                     text="OFF", font=Font(family='times', size=11), background='red',
                     command=lambda: dut["JulaboFP50"].Run_mode(Switch=0)).place(x=50, y=340)
SetT1_Chiller = Button(root, fg="black", width=5,
                       text="Use T1", font=Font(family='times', size=11),
                       command=lambda: dut["JulaboFP50"].Run_mode(SetTemp=0)).place(x=100, y=340)
SetT2_Chiller = Button(root, fg="black", width=5,
                       text="Use T2", font=Font(family='times', size=11),
                       command=lambda: dut["JulaboFP50"].Run_mode(SetTemp=1)).place(x=150, y=340)
GetTinfo_Chiller = Button(root, fg="black", width=12,
                          text="Print Chiller info", font=Font(family='times', size=11),
                          command=lambda: dut["JulaboFP50"].Chiller_mode(Temp=1)).place(x=210, y=340)

# Temprature Reading scale
lblInfo = Label(root, padx=8, font=Font(family='times', size=11, weight='bold'),
                text="==============Temprature Reading scale==============", fg="Black", anchor='w').place(x=12, y=380)

lblInfo = Label(root, padx=8, font=Font(family='times', size=11), text="Temprature (C) =").place(x=12, y=400)
lblTmp = Label(root, font=('times', 11))
lblTmp.place(x=160, y=400)

lblInfo = Label(root, padx=8, font=Font(family='times', size=11), text="Humidity (RH) =").place(x=12, y=425)
lblHum = Label(root, font=('times', 11))
lblHum.place(x=160, y=425)

lblInfo = Label(root, padx=8, font=Font(family='times', size=11), text="Dew point (C) =").place(x=12, y=450)
lblDew = Label(root, font=('times', 11))
lblDew.place(x=160, y=450)

# position reading scale
lblInfo = Label(root, padx=8, font=Font(family='times', size=11), text="Coordinates").place(x=12, y=470)
lblpos = Label(root, font=Font(family='times', size=12))
lblpos.place(x=140, y=470)

t1 = time.time()  # end time
print (t1 - t0)


position1 = ''


def coordinates():
    global position1
    position2 = dut["MotorStage"].get_coordinates()
    if position2 != position1:
        position1 = position2
    lblpos.config(text=position2)
    lblpos.after(1000, coordinates)


coordinates()

Temp1 = ''


def Temp_counter():
    global Temp1
    Temp2 = dut['Thermohygrometer'].get_temperature()
    if Temp2 != Temp1:
        Temp1 = Temp2
        lblTmp.config(text=Temp2[0])
    lblTmp.after(1000, Temp_counter)


Temp_counter()

Hum1 = ''


def Hum_counter():
    global Hum1
    Humidity = [100]
    Hum2 = dut['Thermohygrometer'].get_humidity()
    i = 0
    if Hum2 != Hum1:
        Hum1 = Hum2
        Humidity[i] = Hum2
        i + 1
        lblHum.config(text=Hum2[0])
    lblHum.after(1000, Hum_counter)


Hum_counter()

Dew1 = ''


def Dew_counter():
    global Dew1
    Dew2 = dut['Thermohygrometer'].get_dew_point()
    if Dew2 != Dew1:
        Dew1 = Dew2
        lblDew.config(text=Dew2[0])
    lblDew.after(1000, Dew_counter)


Dew_counter()
root.mainloop()
