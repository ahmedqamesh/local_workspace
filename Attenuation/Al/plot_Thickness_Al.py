from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
Attenuation_Al = [1.128E+00, 5.684E-01,3.681E-01,2.778E-01,2.018E-01]
Energy_range = ['30 Kev','40 Kev','50 Kev','60 Kev','80 Kev']
Al_thickness = 2.8 #Micro
Al_rho = 2.70 #g/cm3
x2=np.arange(0, 0.001, 0.00001)
colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon']
for i in np.arange(len(Attenuation_Al)):
    y_neu_1 = np.exp(- Attenuation_Al[i] * Al_rho * x2)
    y_neu_1_plot, =plt.plot(x2, y_neu_1, ':', color=colors[i], label=Energy_range[i])
plt.grid(True)
ax = plt.gca()  

plt.grid(True)
ax = plt.gca()
#plt.ylim(bottom=-0.01)
plt.xlabel('Al Thickness (cm)')
plt.ylabel('Transmission $I$/$I_0$ ')
plt.axvline(x=Al_thickness*0.0001, linewidth=2, color='#d62728', linestyle='dashed')
plt.legend()
plt.title(r'Transmission of x rays through Al absorber', fontsize=11)
ax.set_xscale('log')
#ax.set_yscale('log')

plt.tight_layout()
plt.savefig(r'Thickness_Al.png', bbox_inches='tight')
plt.show()

