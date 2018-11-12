from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
Attenuation_Al = [2.263E+03,2.621E+01,3.442E+00,1.128E+00, 5.684E-01,3.681E-01,2.778E-01,2.018E-01]
Energy_range = ['2 Kev','10 Kev','20 Kev','30 Kev','40 Kev','50 Kev','60 Kev','80 Kev']
Al_thickness = 2.8 #Micro
xray_Al_filter = 0.015 # cm
Al_rho = 2.70 #g/cm3
x2=np.arange(0, 1, 0.00001) #cm
colors = ['green','black','orange','grey','#006381','#7e0044','black','red','#33D1FF',"maroon"]
for i in np.arange(len(Attenuation_Al)):
    y_neu_1 = np.exp(- Attenuation_Al[i] * Al_rho * x2)
    y_neu_1_plot, =plt.plot(x2, y_neu_1, ':', color=colors[i], label=Energy_range[i])
plt.grid(True)
ax = plt.gca()  
#plt.ylim(bottom=-0.01)
plt.xlabel('Al Thickness (cm)')
plt.ylabel('Transmission $I$/$I_0$ ')
plt.axvline(x=xray_Al_filter, linewidth=2, color='#d62728', linestyle='dashed') #Al_thickness*0.0001
ax.annotate("%5.3f cm"%xray_Al_filter, xy=(xray_Al_filter, 0), xytext=(xray_Al_filter+0.1, 0.2),
    arrowprops=dict(arrowstyle="-|>",
    connectionstyle="arc3,rad=-0.5",relpos=(.2, 0.),fc="w"))
plt.legend(loc='upper right')
plt.title(r'Transmission of x rays through Al absorber', fontsize=11)
ax.set_xscale('log')
#ax.set_yscale('log')

plt.tight_layout()
plt.savefig(r'Thickness_Al_xray_filter.png', bbox_inches='tight')
plt.show()

