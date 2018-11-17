from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

data = loadtxt('mass_attenuation_coeff_in_detail_Cu.dat')
x = data[:, 0]
y = data[:, 6]
Cu_rho = 8.96 #g/cm3
y_neu = 1 - np.exp(- y * Cu_rho * 580*1E-07)  # 200 mum thick Si layer (5.8 nm), 
plt.grid(True)
plt.plot(x*10**3, y_neu, '-', color='black')
ax = plt.gca()
plt.xlim(0, 40)
plt.ylim(bottom=0)
plt.xlabel('Photon energy / keV')
plt.ylabel('Absorption probability')
plt.legend(["Absorption 1-$I$/$I_0$ of $5.8$nm thick cu layer (Z=29)"], loc= 'upper right')
#ax.set_xscale('log')
#ax.set_yscale('log')
plt.tight_layout()
plt.savefig(r'absorption_xray_cu.pdf', bbox_inches='tight')