# pip install matlibplot
#pip install scipy
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
if __name__ == '__main__':
    x = np.arange(0, 50, 1)
    y =  0.5*x+3    
    selected_point = 5
    spline = interpolate.splrep(x, y, s=0, k=1)  # create spline interpolation
    xnew = np.linspace(np.min(x), np.max(x), num = 50, endpoint = True)
    spline_eval = interpolate.splev(xnew, spline)  # evaluate spline
    plt.plot(x,y,'o',xnew,spline_eval,"-")
    plt.axvline(x=selected_point, linewidth=0.8, color="red", linestyle='dashed')
    print("The corresponding value for the point %0.3f is "%selected_point, interpolate.splev(selected_point, spline))
    plt.legend(["data", "Interpolated data"], loc ="upper right")
    plt.show()
    