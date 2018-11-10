from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

data = loadtxt('mass_attenuation_coeff_in_detail_1_100keV_al.dat')
x = data[:, 0]
y = data[:, 6]  # total mass attenuation coeff with coherent scattering
p = data[:, 3]  # mass attenuation coeff due to photoelectric effect
i = data[:, 2]  # mass attenuation coeff due to compton (incoherent) scattering
r = data[:, 1]  # mass attenuation coeff due to rayleigh (coherent) scattering
ppn = data[:, 4]  # mass attenuation coeff due to pair production in nuclei field
ppe = data[:, 5]  # mass attenuation coeff due to pair production in electron field


plt.grid(True)
#ppe_plot, = plt.plot(x*10**3, ppe, ':', color='orange', label='Pair production (electron)')
#ppn_plot, = plt.plot(x*10**3, ppn, ':', color='grey', label='Pair production (nuclei)')
r_plot, = plt.plot(x*10**3, r, ':', color='green', label='Coherent scattering')
i_plot, = plt.plot(x*10**3, i, '-.', color='#006381', label='Compton scattering')
p_plot, = plt.plot(x*10**3, p, '--', color ='#7e0044', label='Photoelectric effect')
y_plot, = plt.plot(x*10**3, y, '-', color='black', label='Total')



ax = plt.gca()
plt.xlim(1, 100)
plt.xlabel('Photon energy / keV')
plt.ylabel('Mass attenuation coefficient / cm$^2$/g')
plt.legend(handles=[y_plot, p_plot, i_plot, r_plot])
#plt.legend(["Total mass attenuation coefficient of Si (Z=14)", "Photoelectric effect", "Compton Scattering", "Coherent scattering", "Pair production", "Pair Production"], loc= 'upper right')
ax.set_xscale('log')
ax.set_yscale('log')
plt.title(r'Mass atenuation coeffecient in Al', fontsize=11)
plt.tight_layout()
plt.savefig(r'mass_attenuation_coeff_in_detail_1_100keV_al_coherentscattering.pdf', bbox_inches='tight')
plt.show()