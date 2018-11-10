from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

x2=np.arange(0, 0.001, 0.00001)
Si_rho = 2.32
si_thicknes = 4.5 #micro
Attenuation_Si = [1.436E+00,7.010E-01,4.385E-01,3.206E-01,2.228E-01]
Energy_range = ['30 Kev','40 Kev','50 Kev','60 Kev','80 Kev']
colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon']
for i in np.arange(len(Attenuation_Si)):
    y_neu_1 = np.exp(- Attenuation_Si[i] * Si_rho * x2)
    y_neu_1_plot, =plt.plot(x2, y_neu_1, ':', color=colors[i], label=Energy_range[i])
plt.grid(True)
ax = plt.gca()
plt.xlabel('Silicon Thickness (cm)')
plt.ylabel('Transmission $I$/$I_0$ ')
plt.legend()
plt.axvline(x=si_thicknes*0.0001, linewidth=2, color='#d62728', linestyle='dashed')
plt.title(r'Transmission of x rays through si Absorber', fontsize=11)
plt.tight_layout()
plt.savefig(r'Thickness_si.png', bbox_inches='tight')


