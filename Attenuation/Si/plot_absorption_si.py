from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

data = loadtxt('mass_attenuation_coeff_si_neu.dat')

x = data[:, 0]
y = data[:, 1]
y_neu = 1 - np.exp(- y * 2.32 * 0.02)  # 200 mum thick Si layer (0.02 cm), Dichte Si 2.32 g cm-3
plt.grid(True)
plt.plot(x, y_neu, '-', color='black')
ax = plt.gca()
plt.xlim(0, 100)
plt.ylim(bottom=0)
plt.xlabel('Photon energy / keV')
plt.ylabel('Absorption probability')
plt.legend(["Absorption 1-$I$/$I_0$ of $200\ $$\mathrm{\mu}$m thick Si layer (Z=14)"], loc= 'upper right')
#ax.set_xscale('log')
#ax.set_yscale('log')
plt.tight_layout()
plt.savefig(r'absorption_xray_si.pdf', bbox_inches='tight')