from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
import csv
Be_rho = 1.85#g/cm3
Be_thickness = 2.8 #Micro
xray_Be_filter = 0.03 # cm
Density =[]
Mu=[]
Energy =[]
y = [] 
with open("Attenuation_Energy_Be.csv", 'r')as parameters:
    colors = ['green','black','orange','grey','#006381','#7e0044','black','red','#33D1FF',"maroon"]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    reader = csv.reader(parameters)
    reader.next()
    x=np.arange(0, 1, 0.00001) #cm
    for row in reader:
        Density = np.append(Density, float(row[0]))
        Mu = np.append(Mu, float(row[1]))
        Energy = np.append(Energy, float(row[2]))
    for i in np.arange(len(Energy)):
        y = np.exp((-1)* Mu[i] * Density[0] * x)
        ax.plot(x, y, ':',color=colors[i],label=str(Energy[i])+'Kev')                    
    ax.grid(True)
    plt.ylim(bottom=-0.01)
    plt.axvline(x=0.03, linewidth=2, color='#d62728', linestyle='dashed')
    ax.set_xlabel('Beryllium Thickness (cm)')
    ax.set_ylabel('Transmission $I$/$I_0$ ')
    ax.annotate("%5.3f cm"%0.03, xy=(0.03, 0), xytext=(0.03+0.1, 0.2),
        arrowprops=dict(arrowstyle="-|>",
        connectionstyle="arc3,rad=-0.5",relpos=(.2, 0.),fc="w"))
    ax.legend(loc='upper right')
    ax.set_title(r'Transmission of x rays through Beryllium absorber', fontsize=11)
    ax.set_xscale('log')
    plt.tight_layout()
    plt.savefig(r'Thickness_Be_xray_filter.png', bbox_inches='tight')
    plt.show()

