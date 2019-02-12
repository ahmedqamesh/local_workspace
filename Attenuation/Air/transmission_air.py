from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

data = loadtxt('mass_attenuation_coeff_air_neu.dat')

x = data[:, 0]
y = data[:, 1] 
plt.grid(True)
plt.plot(x*0.001, y, '-', color='black')
ax = plt.gca()
#plt.xlim(0, 30)
plt.ylim(bottom=0)
plt.xlabel('Photon energy [keV]')
plt.ylabel('Transmission')
ax.set_xscale('log')
#ax.set_yscale('log')
plt.tight_layout()
plt.savefig(r'Transmission_x_ray_air.png', bbox_inches='tight')
