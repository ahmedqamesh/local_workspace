from analysis import analysis
from analysis import plotting
import numpy as np
import logging
#%matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)
import pandas as pd

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

def cablepowerloss(Is=np.arange(0.1,20,0.1),Rc=4):
    '''
  Calculate the cable power loss 
    Is =array of all the possible currents from the power supply in a specific range 
    Rc is the cable resistance as calculated from AWG
    '''
    # calculate the cable voltage drop
    Uc=[Is[i]*Rc for i in range(len(Is))]
    # calculate the cable loss power 
    Pc = np.multiply(Uc,Is)
    return Pc

def cableresistanceTemprature(delta_T=np.arange(10,50,1),Rc=4,alpha=.0039):
    '''
    Calculate the cable power loss 
    T =array of all the possible Temperatures
    Rc is the cable resistance as calculated from AWG
    alpha: Temperature coefficient of resistance
    '''
    return [Rc*(1+alpha*delta_T[i]) for i in range(len(delta_T))]

#if __name__ == '__main__': 
Directory = "DCConverter/"
PdfPages = PdfPages('output_data/DCConverter' + '.pdf')
p =plotting.Plotting()
    
# Stage I calculations
Rc=4 # Cable resistance back and forth
pf=4*5 # FPGA power
fl=1/0.88 # DC/DC converter factor

Is=np.arange(0.5,5,0.01) # all possible currents provided from the source

Us, Trans_eff = voltagesupply(pf=pf,fl=fl,Is=Is,Rc=Rc) # gives source potential and Transmited power (PF/PS *100)
Pc = cablepowerloss(Is=Is,Rc=Rc) # Power Loss in the cables

DataFrame = pd.DataFrame({"Is":Is, "Us":Us,"efficiency":Trans_eff,"Pc":Pc})  
print(DataFrame[145:152])


p.plot_linear(Directory=Directory , PdfPages=PdfPages, x=Is,x_label=r'Delivered current $I_s$ [A]',y=Us,y_label="Output Voltage $U_S$ [V]",
               map=True,z=Trans_eff,z_label="Transferred Efficiency $P_S/P_F$ [%]",
              text=True,txt ="Needed power = %0.1f W \n $R_c$ = %i ohm"%(pf,Rc), 
              test= "Power_supply_voltage",p = [pf, fl,Rc],
              title="Power supply voltage needed [For a DC converter of %i$\%%$ efficiency]"%(1/fl*100),
              line= True, data_line=Pc)
   
# Stage II calculations [PP3 To PP0]
Um1= 1.4 # voltage across Mops <= 2V
Rc2=24 #ohm Cable resistance back and forth [PP3-PP0]
Id=0.025 #A Input current for 1 Mops Id=0.25m after simulation
Uc= Rc2*Id  # Voltage drop across the cable for one MOPS
Uc2=Rc2*Id*2 # Voltage drop across the cable for 2 Mops
Us2 = Uc2 + Um1 # Voltage needed from the power supply
print("2 source Voltage Us = %0.2f V for 2 Mops to achieve %0.2f V per Mops"%(Us2,Um1))
Us_space = np.linspace(Us2-1,Us2+4)
Uc1=Rc2*Id*1 #UC with 1 Mops
Um2= Us_space - Uc1
Limit =Um2-Um1
p.plot_lines(x1= Us_space ,y1 = Um2 ,z1=Limit,Directory=Directory,PdfPages=PdfPages)


#Temperatures coefficient of copper is 0,39%
T0 = 20
T=np.arange(-50,50,2)
delta_T= [T[i]-T0 for i in range(len(T))]   
RT = cableresistanceTemprature(delta_T=delta_T,Rc=Rc2,alpha=.0039)

# A constant Voltage supply
Id=0.4
Uc= Rc2*Id  # = 9.67 is also possible for the voltage

IM=[Uc/RT[i]*1000 for i in range(len(RT))] 
Ps = [IM[i]*Uc/1000 for i in range(len(IM))]
p.plot_linear(Directory=Directory , PdfPages=PdfPages, x=delta_T,x_label=r'$\Delta$T [$^o$C]',y=IM,y_label="Input current from the source [mA]",
              map=False,title="Input current as a function of Temperature for a constant Voltage source",
               text=True,txt =r"Input Voltage V=%0.2f V"%Uc,test= "Temp_Current",
               line= True, data_line=Ps,data_label= "Power consumption [W]")
    
#A constant CURRENT supply
Uc2=[Id*RT[i] for i in range(len(RT))] 
Ps2 = [Id*Uc2[i] for i in range(len(Uc2))]   
p.plot_linear(Directory=Directory , PdfPages=PdfPages, x=delta_T,x_label=r'$\Delta$T [$^o$C]',y=Uc2,y_label="Input voltage from the source [v]",
              map=False,title="Input voltage as a function of Temperature for a constant Voltage source",
               text=True,txt =r"Input Current I=%0.2f A"%0.4,test= "Temp_Current",
               line= True, data_line=Ps2,data_label= "Power consumption [W]")

p.close(PdfPages=PdfPages)



