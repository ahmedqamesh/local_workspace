from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
#http://physics.nist.gov/PhysRefData/XrayMassCoef/tab3.html 3.3.2017 (only mass absorption coeff)
#http://physics.nist.gov/cgi-bin/Xcom/xcom3_1 bzw. http://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html 3.3.2017 (mass abs coeff  with photoeffekt, compton usw..)
data = loadtxt('mass_attenuation_coeff_in_detail_si.dat')
x = data[:, 0]
y = data[:, 6]  # total mass attenuation coeff with coherent scattering
p = data[:, 3]  # mass attenuation coeff due to photoelectric effect
i = data[:, 2]  # mass attenuation coeff due to compton (incoherent) scattering
r = data[:, 1]  # mass attenuation coeff due to rayleigh (coherent) scattering
ppn = data[:, 4]  # mass attenuation coeff due to pair production in nuclei field
ppe = data[:, 5]  # mass attenuation coeff due to pair production in electron field

conversion = 10**3
plt.grid(True)
ppe_plot, = plt.plot(x*conversion, ppe, ':', color='orange', label='Pair production (electron)')
ppn_plot, = plt.plot(x*conversion, ppn, ':', color='grey', label='Pair production (nuclei)')
r_plot, = plt.plot(x*conversion, r, ':', color='green', label='Coherent scattering')
i_plot, = plt.plot(x*conversion, i, '-.', color='#006381', label='Compton scattering')
p_plot, = plt.plot(x*conversion, p, '--', color ='#7e0044', label='Photoelectric effect')
y_plot, = plt.plot(x*conversion, y, '-', color='black', label='Total')



ax = plt.gca()
plt.xlim(1, 10**6)
plt.ylim(ymin=10**(-4))
plt.xlabel('Photon energy / keV')
plt.ylabel('Mass attenuation coefficient / cm$^2$/g')
plt.legend(loc= 'upper right')
ax.set_xscale('log')
ax.set_yscale('log')
plt.tight_layout()
plt.title(r'Mass atenuation coeffecient in Si', fontsize=11)
plt.savefig(r'mass_attenuation_coeff_pb_in_si_with_coherentscattering.pdf', bbox_inches='tight')
