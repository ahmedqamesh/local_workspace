# pip install matlibplot
#pip install scipy
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
import xlrd
from scipy.optimize import curve_fit
from matplotlib import collections as matcoll
if __name__ == '__main__':
    file_location = (r'/home/dcs/Downloads/Bi-energy-spectrum.xlsx')

    workbook    = xlrd.open_workbook(file_location)
    first_sheet = workbook.sheet_by_index(0)
    data_points = first_sheet.nrows - 1
    x  = np.array([float(first_sheet.cell_value(i, 0)) for i in range(1, int(1*data_points))  ])
    y = np.array([float(first_sheet.cell_value(i, 1)) for i in range(1, int(1*data_points))  ])
    fig = plt.figure()
    ax = fig.add_subplot(111)    
    ax.plot(x,y, "o", color="red", markersize=4,  label="Data")
    
    selected_point = 100
    ax.set_yscale("log")
    ax.grid(True)
    
    lines = []
    pair=[(100,0), (100, 22719.8125)]
    lines.append(pair)
    linecoll = matcoll.LineCollection(lines)
    ax.add_collection(linecoll)
    ax.set_xlabel("Qamesh X", fontsize=10)
    ax.set_title("Qamesh TITLE", fontsize=8)
    ax.set_ylabel("Qamesh Y", fontsize=10)
        
    plt.legend(loc ="upper right")
    plt.show()
    