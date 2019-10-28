from analysis import plotting
from analysis import analysis
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import logging
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

if __name__ == '__main__':
    Directory = "DCConverter/"
    PdfPages = PdfPages('output_data/DCConverter' + '.pdf')
    
    # Stage I calculations
    Rc=4
    pf=4*5
    fl=1/0.8
    Is=np.arange(0.1,5,0.01)
    Us, Trans_eff = voltagesupply(pf=pf,fl=fl,Is=Is,Rc=Rc)
    Pc = cablepowerloss(Is=Is,Rc=Rc)
    
    #DataFrame = pd.DataFrame({"Is":Is, "Us":Us,"Transferred efficiency":Trans_eff,"cable power loss":Pc})  
    #print(DataFrame)
        
    p =plotting.Plotting()
    p.plot_linear(Directory=Directory , PdfPages=PdfPages, x=Is,x_label=r'Delivered current $I_s$ [A]',y=Us,y_label="Output Voltage $U_S$ [V]",
                   map=True,z=Trans_eff,z_label="Transferred Efficiency $P_S/P_F$ [%]",
                  text=True,txt ="Needed power = %0.1f W \n $R_c$ = %i ohm"%(pf,Rc), test= "Power_supply_voltage",title="Power supply voltage needed [For a DC converter of %i$\%%$ efficiency]"%(1/fl*100),p = [pf, fl,Rc],
                  line= True, data_line=Pc)
   
    # Stage II calculations

    Rc2=24.4

    
    #We should start with more than 11,76 Volt to achieve 2V on Mops
    #Temperatures coefficient of copper is 0,39%
    T0 = 20
    T=np.arange(-50,50,2)
    delta_T= [T[i]-T0 for i in range(len(T))]   
    RT = cableresistanceTemprature(delta_T=delta_T,Rc=Rc2,alpha=.0039)
    
       
    p.plot_linear(Directory=Directory , PdfPages=PdfPages, x=delta_T,x_label=r'$\Delta$T [$^o$C]',y=RT,y_label="Cable resistance [ohm]",
                  map=False,title="Copper resistance as a function of Temperature",
                   text=True,txt =r"$R=R_0$[1+$\alpha$($T$-$T_0$)]""\n"r"$\alpha = 0.0039$"" \n $R_0$= 24.4 ohm ",test= "Temp_Resistance")
    
    Id=0.4
    Uc= Rc2*Id  # = 9.67 is also possible for the voltage
    # A constant Voltage supply
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
    