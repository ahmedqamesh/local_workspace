from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

data = loadtxt('mass_attenuation_coeff_in_detail_Cu.dat')
x = data[:, 0]
y = data[:, 6]
Cu_rho = 8.96 #g/cm3
y_neu = 1-np.exp(- y * Cu_rho * 5800*1E-07)  # 5800nm thick Si layer  (1E-07 from nano to cm)
plt.grid(True)
plt.plot(x*10**3, y_neu, '-', color='black')
ax = plt.gca()
plt.xlim(0, 50)
plt.ylim(bottom=0)
plt.xlabel('Photon energy / keV')
plt.ylabel('Absorption probability')
plt.legend(["Absorption 1-$I$/$I_0$ of $5.8\mu m$ thick cu layer (Z=29)"], loc= 'upper right')
#ax.set_xscale('log')
#ax.set_yscale('log')
plt.tight_layout()
plt.savefig(r'absorption_xray_cu.pdf', bbox_inches='tight')