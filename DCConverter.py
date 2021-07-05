from analysis import analysis
from analysis import analysisUtils
from analysis import plotting
import numpy as np
import logging
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)
import pandas as pd
import csv
import matplotlib
from celluloid import Camera
from scipy import interpolate
import matplotlib.image as image
import math
# plt.style.use('ggplot')
directory = "DCConverter/"
PdfPages = PdfPages('output_data/DCConverter' + '.pdf')


# http://www.ti.com/lit/an/slyt079/slyt079.pdf
# https://cdn.rohde-schwarz.com/pws/dl_downloads/dl_application/application_notes/1td04/1TD04_0e_RTO_DC-DC-Converter.pdf
# https://www.maximintegrated.com/en/design/technical-documents/tutorials/2/2031.html
# https://www.analog.com/media/en/training-seminars/design-handbooks/Practical-Power-Solutions/Section1.pdf
# https://indico.cern.ch/event/895294/contributions/3775479/attachments/2000763/3339673/Optosystem_PDR.pdf
def cableresistanceTemprature(delta_T=np.arange(10, 50, 1), Rc=4, alpha=.0039):
    '''
    Calculate the cable power loss 
    T =array of all the possible Temperatures
    Rc is the cable resistance as calculated from AWG
    alpha: Temperature coefficient of resistance
    '''
    return [Rc * (1 + alpha * delta_T[i]) for i in range(len(delta_T))]


def plot_risetime(dir=None , files=["cable", "no"], txt="txt", PdfPages=PdfPages, directory=directory, ylim=4000, title="title"):
    im = image.imread(directory + dir + 'icon.png')
    for file in files:
        fig = plt.figure()       
        ax = fig.add_subplot(111)
        x_axis = []
        t_cin = []
        t_cout = []
        t_sin = []
        t_cine = []
        t_coute = []
        t_sine = []
        with open(directory + dir + "risetime/" + file + ".csv", 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            for row in reader:
                x_axis = np.append(x_axis, float(row[0]))
                t_sin = np.append(t_sin, float(row[1]))
                t_sine = np.append(t_sine, float(row[2]))
                t_cin = np.append(t_cin, float(row[3]))
                t_cine = np.append(t_cine, float(row[4]))
                t_cout = np.append(t_cout, float(row[5]))
                t_coute = np.append(t_coute, float(row[6]))                   
        if file.startswith("00_no") is not True:
           ax.errorbar(x_axis, t_sin, yerr=t_sine, color="yellow", fmt='-', markerfacecolor='white', ms=3, label="Rise time of the input signal [before the cable]")
        
        ax.errorbar(x_axis, t_cin, yerr=t_cine, color="green", fmt='-' , markerfacecolor='white', ms=3, label="Rise time of the input signal [after the cable]")
        ax.errorbar(x_axis, t_cout, yerr=t_coute, color="blue", fmt='-', markerfacecolor='white', ms=3, label="Rise time of the output signal")    
        ax.ticklabel_format(useOffset=False)
        ax.legend(loc="upper left", prop={'size': 8})
        ax.set_ylabel("Voltage [V]")
        ax.autoscale(enable=True, axis='x', tight=None)
        ax.set_title(title, fontsize=12)
        # ax.set_ylim([-5,25])
        # ax.set_xlim([-0.04,0])
        ax.grid(True)
        ax.set_xlabel("time $t$ [ms]")
        ax.set_ylabel(r'Voltage [V]')
        fig.figimage(im, 5, 5, zorder=1, alpha=0.08, resize=False)
        plt.tight_layout()
        PdfPages.savefig()
        plt.savefig(directory + dir + file + ".png", bbox_inches='tight')
        plt.clf()

            
def plot_delay_dcconverter(dir=None , test=None, files=["file"], type="", txt="txt", div_delay=[0], output="output", PdfPages=PdfPages, directory=directory, ylim=4000, title="title", logo=True):
    im = image.imread(directory + dir + 'icon.png')
    col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, 5))
    for file in files:
        fig = plt.figure()       
        ax = fig.add_subplot(111)
        x_axis = []
        v_cin = []
        v_cout = []
        v_in = []
        with open(directory + dir + test + file + ".csv", 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            next(reader)
            for row in reader:
                x_axis = np.append(x_axis, float(row[0]) + div_delay[files.index(file)])
                if type.startswith("_no") is not True:
                    v_in = np.append(v_in, float(row[1]))
                    v_cin = np.append(v_cin, float(row[2]))
                    v_cout = np.append(v_cout, float(row[3]))
                else: 
                    v_cin = np.append(v_cin, float(row[1]))
                    v_cout = np.append(v_cout, float(row[2]))                        
        if type.startswith("_no") is not True:
           ax.errorbar(x_axis, v_in, yerr=0.0, color="yellow", fmt='-', markerfacecolor='white', ms=3, label="Power supply voltage  $U_S$ [V]")
        ax.errorbar(x_axis, v_cin, yerr=0.0, color="green", fmt='-' , markerfacecolor='white', ms=3, label="supply voltage to the DC/DC module")
        ax.errorbar(x_axis, v_cout, yerr=0.0, color="blue", fmt='-', markerfacecolor='white', ms=3, label="Output Voltage from the DC/DC module")
        ax.text(0.95, 0.35, files[files.index(file)] + "V", fontsize=10,
                horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))    
        # plt.axvline(x=-4.7227+div_delay[files.index(file)], linewidth=0.8, color="red", linestyle='dashed')
        # plt.axvline(x=-4.7227+div_delay[files.index(file)]+2.04*0.001, linewidth=0.8, color="red", linestyle='dashed')
        # plt.axhline(y=24, linewidth=0.8, color=colors[1], linestyle='dashed')
        ax.ticklabel_format(useOffset=False)
        ax.legend(loc="upper left", prop={'size': 8})
        ax.set_ylabel("Voltage [V]")
        ax.autoscale(enable=True, axis='x', tight=None)
        ax.set_title(title, fontsize=12)
        ax.set_ylim([-5, 25])
        # ax.set_xlim([-0.04,0])
        ax.grid(True)
        ax.set_xlabel("time $t$ [ms]")
        ax.set_ylabel(r'Voltage [V]')
        fig.figimage(im, 5, 5, zorder=1, alpha=0.2, resize=False)
        plt.tight_layout()
        PdfPages.savefig()
        plt.savefig(directory + dir + test + file + type + ".png", bbox_inches='tight')
        plt.clf()
        
    # animation
    cam_fig = plt.figure()
    ax2 = cam_fig.add_subplot(111)
    camera = Camera(cam_fig)  
    for file in files:
        x_axis = []
        v_cin = []
        v_cout = []
        v_in = []
        with open(directory + dir + test + file + ".csv", 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            next(reader)
            next(reader)
            for row in reader:
                x_axis = np.append(x_axis, float(row[0]) + div_delay[files.index(file)])
                if type.startswith("_no") is not True:
                    v_in = np.append(v_in, float(row[1]))
                    v_cin = np.append(v_cin, float(row[2]))
                    v_cout = np.append(v_cout, float(row[3]))    
                else: 
                    v_cin = np.append(v_cin, float(row[1]))
                    v_cout = np.append(v_cout, float(row[2]))   
        if type.startswith("_no") is not True:
            vin = ax2.errorbar(x_axis, v_in, yerr=0.0, color="yellow", fmt='-', markerfacecolor='white', ms=3, label="Power supply voltage  $U_S$ [V]")
        vcin = ax2.errorbar(x_axis, v_cin, yerr=0.0, color="green", fmt='-' , markerfacecolor='white', ms=3, label="supply voltage to the DC/DC module")
        vcout = ax2.errorbar(x_axis, v_cout, yerr=0.0, color="blue", fmt='-', markerfacecolor='white', ms=3, label="Output Voltage from the DC/DC module")
        ax2.text(0.85, 0.35, file + "V", fontsize=10,
            horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))    
        camera.snap()
    # ax2.ticklabel_format(useOffset=False)
    if type.startswith("_no") is not True:
        ax2.legend([vin, vcin, vcout], ["Power supply voltage  $U_S$ [V]", "supply voltage to the DC/DC module", "Output Voltage from the DC/DC module"], loc="upper left", prop={'size': 8})
    else: 
        ax2.legend([vcin, vcout], ["supply voltage to the DC/DC module", "Output Voltage from the DC/DC module"], loc="upper left", prop={'size': 8})
    ax2.set_ylabel("Voltage [V]")
    ax2.autoscale(enable=True, axis='x', tight=None)
    ax2.set_title(title, fontsize=12)
    # ax2.set_ylim([-5,25])
    # ax2.set_xlim([-0.04,0])
    # ax2.get_xaxis().set_ticks([])
    ax2.grid(True)
    ax2.set_xlabel("time $t$ [ms]")
    ax2.set_ylabel(r'Voltage [V]')
    cam_fig.figimage(im, 5, 5, zorder=1, alpha=0.08, resize=False)       
    animation = camera.animate()
    animation.save(directory + dir + test + "00_Animation" + type + ".gif", writer='imagemagick', fps=1)


def plot_ramps(module="LTM8067EY-PBF", dir=None, directory=None, PdfPages=None, file=None, output="Ramp_ups"):
    im = image.imread(directory + module + '/icon.png')
    fig = plt.figure()
    ax = fig.add_subplot(111)  
    Sin = []
    Tin = []
    Tout = []
   # dt  = []
    with open(directory + dir + file, 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        next(reader)
        for row in reader:
            Sin = np.append(Sin, float(row[0]))
            Tin = np.append(Tin, float(row[1]))
            Tout = np.append(Tout, float(row[2]))
          #  dt = np.append(dt, float(row[3]))
    col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, 100))
    ax.set_title('Time signals at different ramp-up speeds [' + module + ', $V_{in}$ =' + dir[-4:-1] + ']', fontsize=12)
    t1 = ax.errorbar(Sin, Tin, yerr=0.0, color="green", fmt='-p', markerfacecolor='white', ms=4, label="Time of Input [$T_{in}$]")
    t2 = ax.errorbar(Sin, Tout, yerr=0.0, color="red", fmt='-p', markerfacecolor='white', ms=4, label="Time of Output [T$_{out}$]")
    # dt = ax.errorbar(Sin, dt, yerr=0.0, color=col_row[60], fmt='-p',  markerfacecolor='white', ms=4, label="Delay signal [$\Delta T$]")
    # scipy.optimize.curve_fit(lambda t,a,b: a*numpy.exp(b*t),  Sin,  Tin)
    ax.grid(True)
    plt.xscale('log')
    # plt.xlim(16000, -50)  # decreasing time
    ax.set_xlabel("Input Ramp up speed [V/s]")
    ax.legend(loc="upper right", prop={'size': 10})
    ax.set_ylabel(r'Time [ms]')
    fig.figimage(im, 5, 5, zorder=1, alpha=0.08, resize=False)
    # plt.show()
    plt.tight_layout()
    plt.savefig(directory + dir + output + ".png", bbox_inches='tight')
    PdfPages.savefig()

    
# rise time
def calc_risetime(RL=5 * 1000, CL=470 * 1e-6, Vin=[0], Vout=[0], IL=1):
    TL = []
    for j in np.arange(0, len(Vout)):
        a = IL * RL
        b = ((a - Vin[0]) / (a - Vout[j]))
        l = math.log(b)
        TL = np.append(TL, RL * CL * l * 1000)
        print("From", Vin[0], " V to ", Vout[j], " V==> The rise time [ms] = ", np.round(TL[j], 3), "ms")
    return TL 


p = plotting.Plotting()
utils = analysisUtils.AnalysisUtils()
#################################################### Stage I calculations [US15 To PP0] ##############################################################
pf = 3.3 * 4
Is = np.arange(0.5, 5, 0.01)
Rc = 4.1
fl = 1 / 0.82
Us, Trans_eff, Pc = utils.voltagesupply(pf=pf,  # FPGA power
                                        fl=fl,  # DC/DC converter factor
                                        Is=Is,  # all possible currents provided from the source
                                        Rc=Rc)  # Cable resistance back and forth
                                        # gives source potential and Transmitted power (PF/PS *100)
DataFrame = pd.DataFrame({"Is":Is, "Us":Us, "efficiency":Trans_eff, "Pc":Pc})  
# print(DataFrame[20:35])

p.plot_linear(directory=directory , PdfPages=PdfPages, x=Is * 1000, x_label=r'Input current $I_s$ [mA]', y=Us, y_label="Source Voltage $U_S$ [V]",
               map=True, z=Trans_eff, z_label="Transferred Efficiency $P_S/P_F$ [%]",
              text=True, txt="FPGA power [$P_F$ ]= %0.1f W \n Cable Resistance [$R_c$] = %i ohm" % (pf, Rc),
              test="Power_supply_voltage", p=[pf, fl, Rc],
              title="Supply Voltage needed [DC module efficiency is %i$\%%$]" % (1 / fl * 100),
              line=True, data_line=Pc)

# #################################################### Stage II calculations [PP3 To PP0]##############################################################
Um1 = 1.5  # voltage across Mops <= 2V
Rc2 = 29.276  # ohm Cable resistance back and forth [PP3-PP0]
Id = 0.035  # A Input current for 1 Mops Id=0.25m after simulation
Uc = Rc2 * Id  # Voltage drop across the cable for one MOPS
Uc2 = Rc2 * Id * 2  # Voltage drop across the cable for 2 Mops
Us2 = Uc2 + Um1  # Voltage needed from the power supply
print("2 source Voltage Us = %0.2f V for 2 Mops to achieve %0.2f V per Mops" % (Us2, Um1))
Us_space = np.linspace(Us2 - 1, Us2 + 4)
Uc1 = Rc2 * Id * 1  # UC with 1 Mops
Um2 = Us_space - Uc1
Limit = Um2 - Um1
#p.plot_lines(x1=Us_space , y1=Um2 , z1=Limit, directory=directory, PdfPages=PdfPages)

Vin = [0]  # np.arange(0,20,0.5)
Vout = np.arange(0, 25, 0.5)
TL = calc_risetime(RL=5 * 1000, CL=470 * 1e-6, Vin=Vin, Vout=Vout)

# #################################################### MOPS Powering#############################################
# Temperatures coefficient of copper is 0,39%
T0 = 20
T = np.arange(-50, 50, 2)
delta_T = [T[i] - T0 for i in range(len(T))]   
RT = cableresistanceTemprature(delta_T=delta_T, Rc=Rc2, alpha=.0039)


plot_ramps(directory=directory ,
           PdfPages=PdfPages, dir="LTM8067EY-PBF/rampup/", file="LTM8067EY-PBF_Rampup_results.csv")   

# plot_risetime(dir =  "AP64500SP-EVM/", files =["00_cable_fpga_risetime", "00_no_fpga_risetime"],txt = "txt",PdfPages=PdfPages,directory=directory,ylim=4000,title="title")

# Efficiency of the module
p.plot_efficiency_dcconverter(directory=directory ,
                            PdfPages=PdfPages,
                            dir="LTM8067EY-PBF/",
                            txt="LTM8067EY-PBF",
                            a=8,
                            file="LTM8067EY-PBF_MoPS_results_update.csv",
                            output="LTM8067EY-PBF_MoPS_results_update_efficiency.png",
                            xlim=[0, 45],
                            title="Efficiency of the isolation module [MOPS powering]")

p.plot_efficiency_dcconverter(directory=directory ,
                            PdfPages=PdfPages,
                            dir="LTM8067EY-PBF/",
                            txt="LTM8067EY-PBF",
                            a=14,
                            file="LTM8067EY-PBF_MoPS_NoCable_update.csv",
                            output="LTM8067EY-PBF_MoPS_NoCable_update_efficiency.png",
                            xlim=[0, 45],
                            title="Efficiency of the isolation module [MOPS powering/No Cables]")
# Current Voltage of Power supply
# # with Resistor
# #module MAXM17536ALY
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages,
                            dir="MAXM17536ALY/", file="MAXM17536ALY_FPGA_Full.csv", output="MAXM17536ALY_FPGA_Full.png", ylim=5000, title="Testing results of the step down module [FPGA powering]")
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages,
                            dir="MAXM17536ALY/", file="MAXM17536ALY_FPGA2_Operation.csv", output="MAXM17536ALY_FPGA2_Operation.png", ylim=4000, title="Testing results of the step down module [FPGA powering]")
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages, dir="MAXM17536ALY/", file="MAXM17536ALY_FPGA1.csv", output="MAXM17536ALY_FPGA1.png", ylim=4000, title="Testing results of the step down module [FPGA powering]")

# #module LTM8067EY-PBF
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages, dir="LTM8067EY-PBF/", file="LTM8067EY-PBF_MoPS_results.csv", output="LTM8067EY-PBF_MoPS_results.png", ylim=100, title="Testing results of the isolation module [MOPS powering]")
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages, dir="LTM8067EY-PBF/", file="LTM8067EY-PBF_MoPS_results_update.csv", output="LTM8067EY-PBF_MoPS_results_update.png", ylim=300, title="Testing results  of the isolation module [MOPS powering]")
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages, dir="LTM8067EY-PBF/", file="LTM8067EY-PBF_MoPS_NoCable_update.csv", output="LTM8067EY-PBF_MoPS_NoCable_update.png", ylim=300, title="Testing results  of the isolation module [MOPS powering/No Cables]")

# Oscilloscope
# plot_delay_dcconverter(dir="LTM8067EY-PBF/", test="/rampup/Agilent E3631A/0000/", txt="LTM8067EY-PBF", files=["RampUp_05Vinput", "RampUp_10Vinput", "RampUp_12Vinput", "RampUp_15Vinput", "RampUp_20Vinput"],
                       # type="_no_mops", div_delay=[0, 0, 0, 0, 0], output="LTM8067EY-PBF_MoPS_update_delay.png",
                       # title="Ramp-Up of the DC/DC converter [LTM8067EY-PBF]")

# #################################################### FPGA Powering#############################################
# Ramp up speed
plot_ramps(directory=directory ,
           PdfPages=PdfPages,
           module="AP64500SP-EVM",
           dir="AP64500SP-EVM/rampup/NOCable/Wiener/20V/",
           file="AP64500SP-EVM_Rampup_results.csv")   

plot_ramps(directory=directory ,
           PdfPages=PdfPages,
           module="AP64500SP-EVM",
           dir="AP64500SP-EVM/rampup/NOCable/Wiener/15V/",
           file="AP64500SP-EVM_Rampup_results.csv") 

# Efficiency of the module 
# # with Resistor
p.plot_efficiency_dcconverter(directory=directory ,
                            PdfPages=PdfPages,
                            dir="AP64500SP-EVM/",
                            txt="AP64500SP-EVM",
                            a=16,
                            file="AP64500SP-EVM_FPGA_Resistors.csv",
                            output="AP64500SP-EVM_FPGA_efficiency_Resistors.png",
                            xlim=[0, 45],
                            title="Efficiency of the step down module [FPGA powering]")
# # without cable
p.plot_efficiency_dcconverter(directory=directory ,
                            PdfPages=PdfPages,
                            dir="AP64500SP-EVM/",
                            txt="AP64500SP-EVM",
                            a=7,
                            file="AP64500SP-EVM_FPGA_NoCable.csv",
                            output="AP64500SP-EVM_FPGA_efficiency_NoCable.png",
                            xlim=[0, 45],
                            title="Efficiency of the step down module [FPGA powering/No Cables]")        
# # with cables
p.plot_efficiency_dcconverter(directory=directory ,
                            PdfPages=PdfPages,
                            dir="AP64500SP-EVM/",
                            txt="AP64500SP-EVM",
                            a=7,
                            file="AP64500SP-EVM_FPGA_Cables.csv",
                            output="AP64500SP-EVM_FPGA_efficiency_Cable.png",
                            xlim=[0, 45],
                            title="Efficiency of the step down module [FPGA powering/60m AWG20 Cable]")     

# Current Voltage of Power supply
# # with Resistor
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages, dir="AP64500SP-EVM/", file="AP64500SP-EVM_FPGA_Resistors.csv", output="AP64500SP-EVM_FPGA_Resistors.png", ylim=4000, title="Testing results of the step down module [FPGA powering]")
# # without cable
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages, dir="AP64500SP-EVM/", file="AP64500SP-EVM_FPGA_NoCable.csv", output="AP64500SP-EVM_FPGA_NoCable.png", ylim=4000, title="Testing results of the step down module [FPGA powering/No Cables]")         

# # with cable
p.plot_voltage_dcconverter(directory=directory ,
                            PdfPages=PdfPages, dir="AP64500SP-EVM/", file="AP64500SP-EVM_FPGA_Cables.csv", output="AP64500SP-EVM_FPGA_Cable.png", ylim=4000, title="Testing results of the step down module [FPGA powering/60m AWG20 Cables]")         


# Oscilloscope
# plot_delay_dcconverter(dir="AP64500SP-EVM/", txt="AP64500SP-EVM", test="/rampup/NOCable/E3631A/0000/", files=["RampUp_11Vinput", "RampUp_15Vinput", "RampUp_20Vinput"],
                       # type="_no_fpga", div_delay=[0, 0, 0, 0, 0], output="AP64500SP-EVM_fpga_update_delay.png",
                        # title="Ramp-Up of the DC/DC converter [AP64500SP-EVM]")

p.close(PdfPages=PdfPages)

