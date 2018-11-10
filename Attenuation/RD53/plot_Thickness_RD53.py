from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

fig =plt.figure()
gs = gridspec.GridSpec(2, 1, height_ratios=[2, 2])
ax = plt.subplot(gs[0])
ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])
def autolabel(rects,total):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax2.text(rect.get_x() + rect.get_width()/2., 1.05*height,'%.2f %%' % (height/total*100), ha='center', va='bottom')
Si_rho = 2.32 #g/cm3
Cu_rho = 8.96 #g/cm3
Al_rho = 2.70 #g/cm3
# Energy deposition from Geant4
Energy_deposition = [70.3885,254.722,55.2842,1.98059*1000,42.7487,394.459,38.6216,82.0917,14.4346,82.8024,14.2578,
               80.9561,13.9143,78.9877,13.6107, 76.8117,13.2364, 74.3392,12.557,54.8731,10.0689] # ev
total_deposition =np.sum(Energy_deposition)
    
Energy_range = ['30 Kev','40 Kev','50 Kev','60 Kev']
Attenuation_Al = [1.128E+00, 5.684E-01,3.681E-01,2.778E-01]
Attenuation_Sio2 = [0.859,0.463,0.318,0.252]
Attenuation_cu = [1.119E-01,9.413E-02,8.363E-02,7.625E-02]
Al_thickness = [2800] # nano 2.8
Cu_thickness = [3400,900,220*6,180] #nano 5.8
Si_thickness = [1000,800,670*2,175*6,310] #nano 4.5
thickness_Micro =[x*1E-03 for x in [1000,2800,800,3400,670,900,670,220,175,220,175,220,175,220,175,220,175,220,175,180,310]] #Micro
thickness = [x*1E-07 for x in [1000,2800,800,3400,670,900,670,220,175,220,175,220,175,220,175,220,175,220,175,180,310]] #cm
total_Thickness =np.sum(thickness_Micro)
total_metal = ["si02","Al","si02", "cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02"]
colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon','black']
for E in np.arange(len(Energy_range)): 
    y=[]
    new_x = []
    att= []
    layer_percent = []
    a =0 
    f = 1
    y_pos = np.arange(len(total_metal))
    # Get the depth as a distance from the first layer
    for i in y_pos:
        new_x = np.append(new_x,round(a, 2))
        a = a+thickness_Micro[i]
        layer_percent = np.append(layer_percent, (thickness_Micro[i]/total_Thickness)*100)
      
    y = np.append(y,f)    
    for i in np.arange(len(thickness_Micro)):    
        if total_metal[i] == "Al":
            att = np.append(att,float(np.exp(- Attenuation_Al[E] * Si_rho* thickness[i])))
            if E == 0 : 
                Al = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[1])
                rect1 = ax2.bar(i, Energy_deposition[i],color=colors[1], align='center', alpha=0.5)
                autolabel(rect1,total_deposition)
        if total_metal[i] == "cu":
            att = np.append(att,float(np.exp(- Attenuation_cu[E] * Cu_rho* thickness[i])))
            if E == 0 : 
                rect2 = ax2.bar(i, Energy_deposition[i],color=colors[2], align='center', alpha=0.5)
                cu = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[2])
                autolabel(rect2,total_deposition)
        if total_metal[i] == "si02": 
            if i <20:
                att = np.append(att,float(np.exp(- Attenuation_Sio2[E] * Si_rho* thickness[i])))
            else:
                new_x = np.append(new_x,new_x[i]+thickness_Micro[-1])
                att = np.append(att,float(np.exp(- Attenuation_Sio2[E] * Si_rho* thickness[i])))

            if E == 0 : 
                sio2 = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[0])
                rect3 = ax2.bar(i, Energy_deposition[i],color=colors[0], align='center', alpha=0.5)
                autolabel(rect3,total_deposition)  
        f = f*att[i]
        y = np.append(y,f)
        
    Energy = ax1.plot(new_x, y, ':',color=colors[E+3], linestyle='dashed', label =Energy_range[E])
    ax1.legend()
#ax.set_xticks(new_x)
#ax.set_xticklabels(new_x, rotation=45)

ax.grid(True,axis='y')
ax.set_xlabel('Layer Thickness ($\mu m $)')
ax.set_ylabel('Transmission $I$/$I_0$ ')
ax.set_title(r'Transmission of x rays through RD53 Metal Layers', fontsize=11)         
#ax.legend(handles =[cu,Al,sio2] , labels =["cu", "Al","sio2"])
ax2.set_yscale('log')
ax2.set_ylabel('Energy deposited [ev]')
ax2.set_xlabel("Layer")
ax2.set_ylim(0.001, 20000)
ax2.legend(prop={'size': 6})
ax2.legend(handles =[rect1,rect2,rect3] , labels =["cu", "Al","sio2"])
ax2.set_title(r'Energy loss of 50 keV x rays through RD53 Metal Layers', fontsize=11)         
ax2.grid(True)
ax2.set_xticks(y_pos)
ax2.set_xticklabels(total_metal, rotation=45 )
plt.tight_layout()
plt.savefig(r'Thickness_RD53.png', bbox_inches='tight')
plt.show()

