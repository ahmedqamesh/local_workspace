from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model

data = loadtxt('attenuation_length_xray.dat')
x_dat = data[:, 0]
y_dat = data[:, 1]
x_offset = np.array([x_dat[0], x_dat[1]-1, x_dat[2]-1.3, x_dat[3]-1.3, x_dat[4], x_dat[5]-1.2, x_dat[6]-1.3, x_dat[7]-1.3, x_dat[8]-1.3, x_dat[9]-1.3, x_dat[10], x_dat[11]-1.1])
y_offset = np.array([y_dat[0]+55, y_dat[1]+65, y_dat[2]+36, y_dat[3]+36, y_dat[4]+36, y_dat[5]+65, y_dat[6]+36, y_dat[7]+36, y_dat[8]+36, y_dat[9]+36, y_dat[10]+36, y_dat[11]+65])

n=[r'', r'$\mathregular{K}^{\mathregular{Fe}}_{\alpha,\beta}$', r'$\mathregular{K}^{\mathregular{Cd}}_{\alpha}$', r'$\mathregular{K}^{\mathregular{Cd}}_{\beta}$', r'', r'$\mathregular{K}^{\mathregular{Cu}}_{\alpha,\beta}$', r'$\mathregular{K}^{\mathregular{Rb}}_{\alpha}$', r'$\mathregular{K}^{\mathregular{Rb}}_{\beta}$', r'$\mathregular{K}^{\mathregular{Mo}}_{\alpha}$', r'$\mathregular{K}^{\mathregular{Mo}}_{\beta}$', r'', r'$\mathregular{K}^{\mathregular{Ti}}_{\alpha,\beta}$']
plt.grid(True)
#plt.errorbar(x_dat, y_dat, yerr=0, fmt='o', color='black')  # plot points with errorbars
plt.plot(x_dat, y_dat, '.', color='#ba0034', markersize=8)
ax = plt.gca()

for i, txt in enumerate(n):
    plt.text(x_offset[i], y_offset[i], txt, size=10)

def func(x, a, b, c):
    return a * x**b + c

gmod = Model(func)
result = gmod.fit(y_dat, x=x_dat, a=0.17, b=2.9, c=0.46)

print(result.fit_report())

dict = result.best_values
a = dict.get('a')
a_err = result.params['a'].stderr
b = dict.get('b')
b_err = result.params['b'].stderr
c = dict.get('c')
c_err = result.params['c'].stderr

x_test = np.arange(0, 30, 1)
plt.plot(x_test, func(x_test, a, b, c), '--', color='black', lw=1)
line_fit_legend_entry = 'fit: ax$^b$+c\na=$%.3f\pm%.3f$\nb=$%.2f\pm%.2f$\nc=$%.2f\pm%.2f$' % (a, a_err, b, b_err, c, c_err)
plt.legend(["data points", line_fit_legend_entry], loc= 'upper left')
plt.legend(["data points"], loc='upper left')




plt.xlim(0, 30)
plt.ylim(0, 2500)
plt.xlabel('Photon energy / keV')
plt.ylabel('Attenuation length in silicon / $\mu$m')
plt.legend(["Data"], loc= 'upper left')
#ax.set_xscale('log')
#ax.set_yscale('log')
plt.tight_layout()
plt.savefig(r'attenuation_length_xray_si_without_fit.pdf', bbox_inches='tight')
