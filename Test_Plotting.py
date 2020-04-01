from analysis import analysis
from analysis import plotting
import numpy as np
import logging
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
from scipy import interpolate
#%matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)
import pandas as pd
import csv
import matplotlib.image as image
plt.style.use('ggplot')

def voltagesupply(pf= 4*5, fl = 1.2, Is=np.arange(0.1,20,0.1),Rc=4):
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
    return Us, Trans_eff

def cableresistanceTemprature(delta_T=np.arange(10,50,1),Rc=4,alpha=.0039):
    '''
    Calculate the cable power loss 
    T =array of all the possible Temperatures
    Rc is the cable resistance as calculated from AWG
    alpha: Temperature coefficient of resistance
    '''
    return [Rc*(1+alpha*delta_T[i]) for i in range(len(delta_T))]

#if __name__ == '__main__': 
directory = "DCConverter/"
PdfPages = PdfPages('output_data/DCConverter' + '.pdf')
p =plotting.Plotting()
    
# Stage I calculations
Rc=4.1 # Cable resistance back and forth
pf=3.3*4 # FPGA power
fl=1/0.82 # DC/DC converter factor

Is=np.arange(0.5,5,0.01) # all possible currents provided from the source
Pc = Pc=[Is[i]*Is[i]*Rc for i in range(len(Is))] # Power Loss in the cables

Us, Trans_eff = voltagesupply(pf=pf,fl=fl,Is=Is,Rc=Rc) # gives source potential and Transmited power (PF/PS *100)

DataFrame = pd.DataFrame({"Is":Is, "Us":Us,"efficiency":Trans_eff,"Pc":Pc})  
#print(DataFrame[20:35])

p.plot_linear(directory=directory , PdfPages=PdfPages, x=Is*1000,x_label=r'Input current $I_s$ [mA]',y=Us,y_label="Output Voltage $U_S$ [V]",
               map=True,z=Trans_eff,z_label="Transferred Efficiency $P_S/P_F$ [%]",
              text=True,txt ="FPGA power [$P_F$ ]= %0.1f W \n Cable Resistance [$R_c$] = %i ohm"%(pf,Rc), 
              test= "Power_supply_voltage",p = [pf, fl,Rc],
              title="Supply Voltage needed [DC module efficiency is %i$\%%$]"%(1/fl*100),
              line= True, data_line=Pc)

# Stage II calculations [PP3 To PP0]
Um1= 1.5 # voltage across Mops <= 2V
Rc2=24 #ohm Cable resistance back and forth [PP3-PP0]
Id=0.035 #A Input current for 1 Mops Id=0.25m after simulation
Uc= Rc2*Id  # Voltage drop across the cable for one MOPS
Uc2=Rc2*Id*2 # Voltage drop across the cable for 2 Mops
Us2 = Uc2 + Um1 # Voltage needed from the power supply
print("2 source Voltage Us = %0.2f V for 2 Mops to achieve %0.2f V per Mops"%(Us2,Um1))
Us_space = np.linspace(Us2-1,Us2+4)
Uc1=Rc2*Id*1 #UC with 1 Mops
Um2= Us_space - Uc1
Limit =Um2-Um1
p.plot_lines(x1= Us_space ,y1 = Um2 ,z1=Limit,directory=directory,PdfPages=PdfPages)


#Temperatures coefficient of copper is 0,39%
T0 = 20
T=np.arange(-50,50,2)
delta_T= [T[i]-T0 for i in range(len(T))]   
RT = cableresistanceTemprature(delta_T=delta_T,Rc=Rc2,alpha=.0039)


def plot_efficiency_dcconverter(dir = None , txt = "txt", a = 8 , file =None, output="output",PdfPages=PdfPages,directory=directory,xlim=[5,40],title="title", logo = True):
    im = image.imread(directory+dir+'icon.png')
    col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, 5))
    v_sin = []
    V_cin = []
    v_cout = []
    I_sin = []
    I_sin_err=[]
    I_cout = []
    I_cout_err=[]    
    f = 1000 #to convert to mA
    efficiency = []
    with open(directory + dir+ file, 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        next(reader)
        for row in reader:
            v_sin = np.append(v_sin, float(row[0]))
            V_cin = np.append(V_cin, float(row[1]))
            
            v_cout = np.append(v_cout, float(row[2]))
            
            I_sin = np.append(I_sin, float(row[3])*f)
            I_sin_err = np.append(I_sin_err, float(row[4])*f)
            
            I_cout = np.append(I_cout, float(row[5])*f)
            I_cout_err = np.append(I_cout_err, float(row[6])*f)
            if float(row[2]) != 0:
                efficiency = np.append(efficiency, float(row[2])*float(row[5])*100/(float(row[0])*float(row[3])))
            else: 
                efficiency = np.append(efficiency, 0)

    fig = plt.figure()
    ax = fig.add_subplot(111)   
    spline = interpolate.splrep(v_sin[a:],efficiency[a:], s=10, k=2)  # create spline interpolation
    xnew = np.linspace(np.min(v_sin[a:]), np.max(v_sin[a:]), num = 50, endpoint = True)
    spline_eval = interpolate.splev(xnew, spline)  # evaluate spline
    plt.plot(v_sin[a:],efficiency[a:],'o',xnew,spline_eval,"-")
    ax.ticklabel_format(useOffset=False)
    ax.grid(True)
    ax.text(0.95, 0.35, txt, fontsize=8,
            horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))    
    ax.set_ylabel("efficiency [%]")
    ax.set_xlabel("Power Supply Voltage $U_S$ [V]")
    ax.autoscale(enable=True, axis='x', tight=None)
    ax.set_title(title, fontsize=12)
    ax.set_xlim(xlim)
    ax.set_ylim([0,100])
    fig.figimage(im, 5, 5, zorder=1, alpha=0.08, resize =False)
    plt.tight_layout()
    plt.savefig(directory + dir+ output, bbox_inches='tight')
    PdfPages.savefig()
        

def plot_voltage_dcconverter(dir = None , file =None, txt = "txt",  output="output",PdfPages=PdfPages,directory=directory,ylim=4000,title="title", logo = True):
    im = image.imread(directory+dir+'icon.png')
    
    col_row = plt.cm.BuPu(np.linspace(0.3, 0.9, 5))
    v_sin = []
    v_cin = []
    v_cout = []
    I_sin = []
    I_sin_err=[]
    I_cout = []
    I_cout_err=[]    
    f = 1000 #to convert to mA
    with open(directory + dir+ file, 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        next(reader)
        for row in reader:
            v_sin = np.append(v_sin, float(row[0]))
            v_cin = np.append(v_cin, float(row[1]))
            v_cout = np.append(v_cout, float(row[2]))
            
            I_sin = np.append(I_sin, float(row[3])*f)
            I_sin_err = np.append(I_sin_err, float(row[4])*f)
            
            I_cout = np.append(I_cout, float(row[5])*f)
            I_cout_err = np.append(I_cout_err, float(row[6])*f)
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 2])
    ax = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1])        
    cmap = plt.cm.get_cmap('viridis', 15)
   # ax.errorbar(v_sin, v_cin, yerr=0.0, color=col_row[0], fmt='-p', markerfacecolor='white', markeredgecolor=col_row[0], ms=4, label="Input Voltage to the DC/DC module")
    ax.errorbar(v_sin, v_cout, yerr=0.0, color=col_row[3], fmt='-p' ,  markerfacecolor='white', markeredgecolor=col_row[3], ms=4, label="Output Voltage from the DC/DC module")
    #ax.plot(v_sin, v_cin , color=col_row[0], label="Input Voltage to the module")
    ax.plot(v_sin, v_cout, color=col_row[3])
    ax.text(0.95, 0.35, txt, fontsize=8,
            horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))    
    ax.ticklabel_format(useOffset=False)
    ax.grid(True)
    ax.legend(loc="upper left", prop={'size': 8})
    ax.set_ylabel("Voltage [V]")
    ax.set_ylim([-0.5,5])
    ax.autoscale(enable=True, axis='x', tight=None)
    ax.set_title(title, fontsize=12)
    
    ax1.errorbar(v_sin, I_sin, yerr=I_sin_err, color=col_row[0], fmt='-p',  markerfacecolor='white', ms=4, label="Input Current")
    ax1.errorbar(v_sin, I_cout, yerr=I_cout_err,  color=col_row[3], fmt='-p' , ms=4,  markerfacecolor='white', label="Load Current by the module")
    
    ax1.plot(v_sin, I_sin , color=col_row[0])
    ax1.plot(v_sin, I_cout, color=col_row[3])
    
    
    ax1.grid(True)
    ax1.set_xlabel("Power Supply Voltage $U_S$ [V]")
    ax1.set_ylabel(r'Current I [mA]')
    ax1.set_ylim([-10,ylim])
    ax1.legend(loc="upper left", prop={'size': 8})
    fig.figimage(im, 5, 5, zorder=1, alpha=0.08, resize =False)
    plt.tight_layout()
    plt.savefig(directory + dir+ output, bbox_inches='tight')
    PdfPages.savefig()
    
# Efficiency of the module
plot_efficiency_dcconverter(dir = "LTM8067EY-PBF/", txt = "LTM8067EY-PBF", a = 8, file="LTM8067EY-PBF_MoPS_results_update.csv",output="LTM8067EY-PBF_MoPS_results_update_efficiency.png",xlim = [0,45], title = "Efficiency of the isolation module [MOPS powering]")
plot_efficiency_dcconverter(dir = "LTM8067EY-PBF/", txt = "LTM8067EY-PBF", a = 14, file="LTM8067EY-PBF_MoPS_NoCable_update.csv", output="LTM8067EY-PBF_MoPS_NoCable_update_efficiency.png",xlim = [0,45], title = "Efficiency of the isolation module [MOPS powering/No Cables]")
plot_efficiency_dcconverter(dir = "AP64500SP-EVM/",txt = "AP64500SP-EVM",a = 16, file="AP64500SP-EVM_FPGA_results.csv",output="AP64500SP-EVM_FPGA_efficiency.png",xlim = [0,45], title = "Efficiency of the step down module [FPGA powering]")
plot_efficiency_dcconverter(dir = "AP64500SP-EVM/",txt = "AP64500SP-EVM",a = 7, file="AP64500SP-EVM_FPGA_NoCable.csv", output="AP64500SP-EVM_FPGA_NoCable_efficiency.png",xlim = [0,45], title = "Efficiency of the step down module [FPGA powering/No Cables]")
       
 # Current Voltage of Power supply
#plot_voltage_dcconverter(dir = "MAXM17536ALY/", txt = "MAXM17536ALY",file="MAXM17536ALY_FPGA_Full.csv",output="MAXM17536ALY_FPGA_Full.png",ylim = 5000,title ="Testing results of the step down module [FPGA powering]")
#plot_voltage_dcconverter(dir = "MAXM17536ALY/", txt = "MAXM17536ALY",file="MAXM17536ALY_FPGA2_Operation.csv",output="MAXM17536ALY_FPGA2_Operation.png",ylim = 4000,title ="Testing results of the step down module [FPGA powering]")
#plot_voltage_dcconverter(dir = "MAXM17536ALY/", txt = "MAXM17536ALY",file="MAXM17536ALY_FPGA1.csv",output="MAXM17536ALY_FPGA1.png",ylim = 4000,title ="Testing results of the step down module [FPGA powering]")

plot_voltage_dcconverter(dir = "LTM8067EY-PBF/", txt = "LTM8067EY-PBF",file="LTM8067EY-PBF_MoPS_results.csv",output="LTM8067EY-PBF_MoPS_results.png",ylim = 100, title = "Testing results of the isolation module [MOPS powering]")
plot_voltage_dcconverter(dir = "LTM8067EY-PBF/", txt = "LTM8067EY-PBF",file="LTM8067EY-PBF_MoPS_results_update.csv", output="LTM8067EY-PBF_MoPS_results_update.png",ylim = 300, title = "Testing results  of the isolation module [MOPS powering]")
plot_voltage_dcconverter(dir = "LTM8067EY-PBF/", txt = "LTM8067EY-PBF",file="LTM8067EY-PBF_MoPS_NoCable_update.csv", output="LTM8067EY-PBF_MoPS_NoCable_update.png",ylim = 300, title = "Testing results  of the isolation module [MOPS powering/No Cables]")

plot_voltage_dcconverter(dir = "AP64500SP-EVM/", txt = "AP64500SP-EVM",file="AP64500SP-EVM_FPGA_results.csv",output="AP64500SP-EVM_FPGA.png",ylim = 4000, title = "Testing results of the step down module [FPGA powering]")
plot_voltage_dcconverter(dir = "AP64500SP-EVM/", txt = "AP64500SP-EVM",file="AP64500SP-EVM_FPGA_NoCable.csv", output="AP64500SP-EVM_FPGA_NoCable.png",ylim = 4000, title = "Testing results of the step down module [FPGA powering/No Cables]")
            
p.close(PdfPages=PdfPages)



