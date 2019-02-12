from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

data = loadtxt('mass_attenuation_coeff_si_neu.dat')

x = data[:, 0]
y = data[:, 1]
d = 150 # 4.5 mum thick Si layer (0.005 cm), density Si 2.32 g cm-3
y_neu = 1 - np.exp(- y * 2.32 * d*1E-04)  
plt.grid(True)
plt.plot(x, y_neu, '-', color='black')
ax = plt.gca()
plt.xlim(0, 60)
plt.ylim(bottom=0)
plt.xlabel('Photon energy / keV')
plt.ylabel('Absorption probability')
plt.legend(["Attenuation  of %.1f$\mathrm{\mu}$m thick Si layer (Z=14)"%d], loc= 'upper right')
#ax.set_xscale('log')
#ax.set_yscale('log')
plt.tight_layout()
plt.savefig(r'absorption_xray_si_%.1fmu.pdf'%d, bbox_inches='tight')
