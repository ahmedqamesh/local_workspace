from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np

Be_density = 1.85
x2=np.arange(0, 10, 0.001)
y_neu_6 = np.exp(- 7.470E+01 * Be_density * x2) #2
y_neu_7 = np.exp(- 6.466E-01 * Be_density * x2) #10
y_neu_8 = np.exp(- 2.251E-01 * Be_density * x2) #20

y_neu_1 = np.exp(- 1.792E-01 * Be_density * x2) #30
y_neu_2 = np.exp(- 1.640E-01 * Be_density * x2) #40
y_neu_3 = np.exp(- 1.554E-01 * Be_density * x2) #50
y_neu_4 = np.exp(- 1.493E-01 * Be_density * x2) #60
y_neu_5 = np.exp(- 1.401E-01 * Be_density * x2) #80 
y_neu_6_plot, =plt.plot(x2, y_neu_6, ':', color='#7e0044', label='2 Kev')
y_neu_7_plot, =plt.plot(x2, y_neu_7, ':', color='#006381', label='10 Kev')
y_neu_8_plot, =plt.plot(x2, y_neu_8, ':', color='maroon', label='20 Kev')
y_neu_1_plot, =plt.plot(x2, y_neu_1, ':', color='orange', label='30 Kev')
y_neu_2_plot, =plt.plot(x2, y_neu_2, ':', color='grey', label='40 Kev')
y_neu_3_plot, =plt.plot(x2, y_neu_3, '--', color='green', label='50 Kev')

plt.grid(True)
ax = plt.gca()
#plt.xlim(0, 100)
plt.ylim(bottom=-0.01)
plt.axvline(x=0.03, linewidth=2, color='#d62728', linestyle='solid')
plt.xlabel('Beryllium Thickness (cm)')
plt.ylabel('Transmission $I$/$I_0$ ')
#plt.ylabel('$\mu$/$\\rho$  /  cm$^2$/g')
plt.legend(handles=[y_neu_6_plot, y_neu_7_plot, y_neu_8_plot, y_neu_1_plot, y_neu_2_plot, y_neu_3_plot])
plt.title(r'Transmission of x rays through Beryllium absorber', fontsize=11)
ax.set_xscale('log')
#ax.set_yscale('log')

plt.tight_layout()
plt.savefig(r'Thickness_Be.png', bbox_inches='tight')
plt.show()

