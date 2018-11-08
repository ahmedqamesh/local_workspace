from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
x2=np.arange(0, 10, 0.001)
y_neu_1 = np.exp(- 1.128E+00 * 2.70 * x2) #30
y_neu_2 = np.exp(- 5.684E-01 * 2.70 * x2) #40
y_neu_3 = np.exp(- 3.681E-01 * 2.70 * x2) #50
y_neu_4 = np.exp(- 2.778E-01 * 2.70 * x2) #60
y_neu_5 = np.exp(- 2.018E-01 * 2.70 * x2) #80
y_neu_1_plot, =plt.plot(x2, y_neu_1, ':', color='orange', label='30 Kev')
y_neu_2_plot, =plt.plot(x2, y_neu_2, ':', color='grey', label='40 Kev')
y_neu_3_plot, =plt.plot(x2, y_neu_3, '--', color='green', label='50 Kev')
y_neu_4_plot, =plt.plot(x2, y_neu_4, '--', color='#006381', label='60 Kev')
y_neu_5_plot, =plt.plot(x2, y_neu_5, '-.', color ='#7e0044', label='80 Kev')

print "how much one need in cm to get 10e-9 = ",  20.7232658369/(2.778E-01 * 2.7) # in Al 31.4 cm


plt.grid(True)
ax = plt.gca()  

plt.ylim(bottom=-0.01)
plt.xlabel('Aluminum Thickness (cm)')
plt.ylabel('Transmission $I$/$I_0$ ')
#plt.ylabel('$\mu$/$\\rho$  /  cm$^2$/g')
plt.legend(handles=[y_neu_1_plot, y_neu_2_plot, y_neu_3_plot, y_neu_4_plot, y_neu_5_plot])
plt.title(r'Transmission of x rays through Aluminum Filter', fontsize=11)
ax.set_xscale('log')
#ax.set_yscale('log')
plt.xlim(0.0001, 10)
plt.tight_layout()
plt.savefig(r'Thickness_Al.png', bbox_inches='tight')
plt.show()

