import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

x1 = np.array(range(0, 4100, 100), dtype=np.float32)
y1 = [0.002, 0.021, 0.040, 0.059, 0.079, 0.098, 0.117, 0.136, 0.156, 0.175, 0.194, 0.213, 0.233, 0.252, 0.271, 0.290, 0.309, 0.329, 0.348, 0.367, 0.386, 0.407, 0.427, 0.446,
      0.465, 0.484, 0.504, 0.523, 0.542, 0.561, 0.580, 0.599, 0.619, 0.638, 0.657, 0.676, 0.695, 0.715, 0.734, 0.753, 0.772]  # in Volts

y2 = [0.0019, 0.021, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.177, 0.197, 0.216, 0.236, 0.255, 0.274, 0.294, 0.313, 0.333, 0.352, 0.372, 0.391, 0.411, 0.431, 0.450, 0.470, 0.489, 0.509,
      0.529, 0.548, 0.568, 0.588, 0.607, 0.627, 0.646, 0.666, 0.686, 0.706, 0.726, 0.746, 0.766, 0.786]  # in Volts
p = 1000
y1_array = p * np.array(y1, dtype=np.float32)  # in mV
y2_array = p * np.array(y2, dtype=np.float32)  # in mV


def lin(x, m, c):
    return m * x + c


line1 = plt.scatter(x1, y1_array, s=50, facecolors='none', edgecolors='r', label='High Injection Voltage')
line2 = plt.scatter(x1, y2_array, s=50, marker='s', facecolors='g', edgecolors='g', label='Medium Injection Voltage')
popt1, pcov = curve_fit(lin, x1, y1_array)
popt2, pcov = curve_fit(lin, x1, y2_array)

plt.plot(x1, lin(x1, *popt1), 'r-', label='Fit: m=%5.3f, c=%5.3f' % tuple(popt1))
plt.plot(x1, lin(x1, *popt2), 'g-', label='Fit: m=%5.3f, c=%5.3f' % tuple(popt2))

ax = plt.gca()
plt.ticklabel_format(useOffset=False)
plt.xlim(0, 4200)
plt.ylim(0, 1200)
plt.title(r'RD53A, Chip SN:0x0751', fontsize=11)
plt.xlabel('InjV$_{Cal}$ Setting')
plt.ylabel('DAC output Voltage [mV]')
#ax.text(0.15, 0.85, '$V^{ADC IN}_{REF}=0.75V$',horizontalalignment='left',verticalalignment='top',transform=ax.transAxes)
plt.legend()
#plt.savefig(r'/home/silab62/HEP/Scripts/Scripts/Tests/INJVCal.png', bbox_inches='tight')
plt.show()
