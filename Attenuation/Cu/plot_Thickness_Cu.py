from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
Attenuation_cu = [1.119E-01,9.413E-02,8.363E-02,7.625E-02,6.606E-02]
Energy_range = ['30 Kev','40 Kev','50 Kev','60 Kev','80 Kev']
Copper_thicknes = 5.8 #micro
Copper_rho = 8.96 #g/cm3
x2=np.arange(0, 0.001, 0.00001)
colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon']
for i in np.arange(len(Attenuation_cu)):
    y_neu_1 = np.exp(- Attenuation_cu[i] * Copper_rho * x2)
    y_neu_1_plot, =plt.plot(x2, y_neu_1, ':', color=colors[i], label=Energy_range[i])

plt.grid(True)
ax = plt.gca()
#plt.ylim(bottom=-0.01)
plt.xlabel('Cu Thickness (cm)')
plt.ylabel('Transmission $I$/$I_0$ ')
plt.axvline(x=Copper_thicknes*0.0001, linewidth=2, color='#d62728', linestyle='dashed')
plt.legend()
plt.title(r'Transmission of x rays through copper absorber', fontsize=11)
ax.set_xscale('log')
#ax.set_yscale('log')

plt.tight_layout()
plt.savefig(r'Thickness_Cu.png', bbox_inches='tight')
plt.show()

