import sys
import os
import os
from validators import length
import sys
import numpy as np
import logging
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger("PP3 calculations")
import pandas as pd
import csv
import matplotlib
from celluloid import Camera
from scipy import interpolate
import matplotlib.image as image
import math
rootdir = os.path.dirname(os.path.abspath(__file__))
root_dir = rootdir + "/"
output_dir = rootdir+"/output_dir/"

from plot_style import *

def plot_supply_voltage(text=False, txt="Text",
                x=np.arange(1, 10), y=np.arange(1, 10), show=False,
                z=np.arange(1, 10), title=None, 
                p=[1, 2, 3],
                data_line=[0], data_label='Power loss in the cable $P_c$ [W]'):
    logger.info(f' Plotting: Supply voltage from power supply')
    fig, ax = plt.subplots()
    cmap = plt.cm.get_cmap('viridis', 15)
    sc = ax.scatter(x, y, c=z, cmap=cmap, s=8)
    cbar = fig.colorbar(sc, ax=ax, orientation='horizontal')
    cbar.ax.invert_xaxis()
    cbar.set_label("Transferred Efficiency $P_S/P_F$ [%]", labelpad=1)
    ax.set_xlabel(r'Input current $I_s$ [mA]')
    ax.set_title(title)
    ax.set_ylabel("Source Voltage $U_S$ [V]")
    ax.ticklabel_format(useOffset=False)
    ax.grid(True)
    if text:
        ax.text(0.95, 0.15, txt,
                horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))          
    # Create axes for loss and voltage 
    ax2 = ax.twinx()
    ax2.errorbar(x, data_line, xerr=0.0, yerr=0.0, color=col_row[3], fmt='o',  ecolor='black', label =  "Power loss")  # plot power loss
    ax2.yaxis.label.set_color(col_row[3])
    ax2.tick_params(axis='y', color=col_row[3])
    ax2.spines['right'].set_position(('outward', 3))  # adjust the position of the second axis 
    ax2.set_ylabel(data_label, rotation=90) 
    plt.tight_layout() 
    plt.savefig(root_dir + "/Power_supply_voltage.pdf", bbox_inches='tight')
    PdfPages.savefig()  
    plt.tight_layout()
    plt.clf() 
    plt.close(fig)
    
def plot_voltage_mops( x1=None, y1=None, z1=None, root_dir=None, PdfPages=PdfPages):
    '''
    PLot a relation between two variables 
    '''
    fig, ax = plt.subplots()
    cmap = plt.cm.get_cmap('viridis', 15)
    logger.info("Plotting Voltage across one Mops $U_M$ [V] When the other one is disconnected")
   # x =[x1[i]/x1[i]*2 for i in range(len(x1))]
    # ax.fill_between(x1-1, x,1.4,facecolor='yellow', alpha=0.5)
    sc = ax.scatter(x1, y1, c=z1, cmap=cmap, s=10)
    cbar = fig.colorbar(sc, ax=ax, orientation='vertical')
    cbar.set_label("Voltage limits [V]", labelpad=1)
    plt.axvline(x=2.6, linewidth=0.8, color="red", linestyle='dashed')
    ax.set_ylabel("Mops Voltage $U_M$ [v]")
    ax.set_title("Voltage across one Mops $U_M$ [V] When the other one is disconnected")
    ax.set_xlabel("Supply Voltage $U_S^{}$ [V]")
    ax.ticklabel_format(useOffset=False)
    ax.grid(True)
    plt.savefig(root_dir + "/Mops_voltage_drop.pdf", bbox_inches='tight')
    PdfPages.savefig()  
    plt.tight_layout()
    plt.clf() 
    plt.close(fig)

def plot_crate_consumption( file_name=None, text_enable=True):
    fig, ax = plt.subplots()
    v_sin = []
    N_cic = []
    Iin = []
    Ierr = []
    P  = []
    with open(root_dir + "/"+file_name + ".csv", 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        next(reader)
        for row in reader:
            v_sin = np.append(v_sin, float(row[0]))
            N_cic = np.append(N_cic, float(row[1]))
            Iin = np.append(Iin, float(row[2]))
            Ierr = np.append(Ierr, float(row[3]))
            P = np.append(P, float(row[4]))
            
    logger.info(f' Plotting: Crate Consumption')
    t1 = ax.errorbar(N_cic, P, yerr=Ierr, color=col_row[3], fmt='-o', label="Crate Consumption")
    ax.grid(True)   
    ax.set_xlabel("# CIC")
    ax.legend(loc="upper right")
    ax.set_ylabel(r'Power [W]')
    if text_enable: ax.set_title('Crate consumption')
    plt.savefig(root_dir + "/"+ file_name + ".pdf", bbox_inches='tight')
   
    ax.set_title('Crate consumption')
    PdfPages.savefig()  
    plt.tight_layout()
    plt.clf() 
    plt.close(fig)

# http://www.ti.com/lit/an/slyt079/slyt079.pdf
# https://cdn.rohde-schwarz.com/pws/dl_downloads/dl_application/application_notes/1td04/1TD04_0e_RTO_DC-DC-Converter.pdf
# https://www.maximintegrated.com/en/design/technical-documents/tutorials/2/2031.html
# https://www.analog.com/media/en/training-seminars/design-handbooks/Practical-Power-Solutions/Section1.pdf
# https://indico.cern.ch/event/895294/contributions/3775479/attachments/2000763/3339673/Optosystem_PDR.pdf
def voltagesupply(pf=None, fl = None, Is=None,Rc=None):
    '''
    The function will print the needed voltage supply from the power supply.
    Pf is FPGA power
    eff is the converter efficiency
    Is =array of all the possible currents in a specific range 
    Rc is the cable resistance as calculated from AWG
    '''
    # calculate the proposed power voltage
    Us =  (pf * fl/Is + Rc * Is)
    
    # calculate the transfered efficiency
    Ps= np.multiply(Is,Us)
    Trans_eff=[pf*100/Ps[i] for i in range(len(Ps))]
    Pc = [Is[i]*Is[i]*Rc for i in range(len(Is))] # Power Loss in the cables
    return Us, Trans_eff, Pc

def calc_cableresistance_temprature(delta_T=np.arange(10, 50, 1), Rc=4, alpha=.0039):
    '''
    Calculate the cable power loss 
    T =array of all the possible Temperatures
    Rc is the cable resistance as calculated from AWG
    alpha: Temperature coefficient of resistance
    '''
    return [Rc * (1 + alpha * delta_T[i]) for i in range(len(delta_T))]

# rise time
def plot_risetime(RL=5 * 1000, CL=470 * 1e-6, Vin=[0], Vout=[0], IL=1):
    TL = []
    for j in np.arange(0, len(Vout)):
        a = IL * RL
        b = ((a - Vin[0]) / (a - Vout[j]))
        l = math.log(b)
        TL = np.append(TL, RL * CL * l * 1000)
    logger.info("Plotting the rise time")
    fig, ax = plt.subplots()
    ax.errorbar(Vout, TL, xerr=0.0, yerr=0.0, fmt='o', color='black', ecolor='black', label = "Rise Time")
    ax.plot(Vout, TL)
    ax.legend(loc="upper right")
    ax.set_xlabel("Voltage [V]")
    ax.set_ylabel("Rise Time [ms]")
    ax.ticklabel_format(useOffset=False)
    ax.grid(True)
    plt.savefig(root_dir + "/"+ "risetime.pdf", bbox_inches='tight')
    ax.set_title('Rise Time')
    PdfPages.savefig()  
    plt.tight_layout()
    plt.clf() 
    plt.close(fig)
    return TL 

# Main function
if __name__ == '__main__':
    # get program arguments
    PdfPages = PdfPages(root_dir+'mopshub_pp3_calculations.pdf')  
    plot_crate_consumption( file_name="crate_consumption", text_enable=False)  
    
    #################################################### Stage I calculations [US15 To PP0] ##############################################################
    pf = 0.5 * 5
    Is = np.arange(0.5, 5, 0.01)
    Rc = 4.1
    fl = 1 / 0.82
    Us, Trans_eff, Pc = voltagesupply(pf=pf,    # FPGA power
                                      fl=fl,  # DC/DC converter factor
                                      Is=Is,  # all possible currents provided from the source
                                      Rc=Rc)  # Cable resistance back and forth
                                              # gives source potential and Transmitted power (PF/PS *100)
    DataFrame = pd.DataFrame({"Is":Is, "Us":Us, "efficiency":Trans_eff, "Pc":Pc})  
    
    plot_supply_voltage( x=Is * 1000,y=Us,z=Trans_eff,
              text=True, txt="FPGA power [$P_F$ ]= %0.1f W \n Cable Resistance [$R_c$] = %i ohm" % (pf, Rc),
              p=[pf, fl, Rc],
              title="Supply Voltage needed [DC module efficiency is %i$\%%$]" % (1 / fl * 100), data_line=Pc)
    
    Um1 = 1.5      # voltage across Mops <= 2V
    Rc2 = 29.276  # ohm Cable resistance back and forth [PP3-PP0]
    Id = 0.035  # A Input current for 1 Mops Id=0.25m after simulation
    Uc = Rc2 * Id  # Voltage drop across the cable for one MOPS
    Uc2 = Rc2 * Id * 2  # Voltage drop across the cable for 2 Mops
    Us2 = Uc2 + Um1  # Voltage needed from the power supply
    Us_space = np.linspace(Us2 - 1, Us2 + 4)
    Uc1 = Rc2 * Id * 1  # UC with 1 Mops
    Um2 = Us_space - Uc1
    Limit = Um2 - Um1
    logger.info("2 source Voltage Us = %0.2f V for 2 Mops to achieve %0.2f V per Mops" % (Us2, Um1))
    plot_voltage_mops(x1=Us_space , y1=Um2 , z1=Limit, root_dir=root_dir, PdfPages=PdfPages)
    plot_risetime(RL=5 * 1000, CL=470 * 1e-6, Vin=[0], Vout=np.arange(0, 25, 0.5))

    # Temperatures coefficient of copper is 0,39%
    T0 = 20
    T = np.arange(-50, 50, 2) 
    RT = calc_cableresistance_temprature(delta_T=[T[i] - T0 for i in range(len(T))], Rc=Rc2)
    
    PdfPages.close()