import numpy as np
from matplotlib import gridspec
import matplotlib.cbook as cbook
import matplotlib.image as image
import matplotlib.pyplot as plt
import pandas as pd
import csv
import matplotlib
from scipy import interpolate
import matplotlib.image as image
import math

fig = plt.figure()
ax = fig.add_subplot(111)
cmap = plt.cm.get_cmap('viridis', 15)
x = np.arange(0,100)
print(type(x))
plt.plot(x,np.arange(0,100))
ax.set_ylabel("Mops Voltage $U_M$ [v]", fontsize=10)
ax.set_title("Voltage across one Mops $U_{M1}^{n10}$ [V] When the other one is disconnected", fontsize=8)
ax.set_xlabel("Supply Voltage  $U_{M}^{n}$  [V]", fontsize=10)
ax.ticklabel_format(useOffset=False)
ax.set_xticks(range(0, 100,5))
ax.set_xticklabels(["$U_{M}^{n}$"]*20)
ax.grid(True)
plt.show()