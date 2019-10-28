from analysis import plotting
from analysis import analysis
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)
import pandas as pd

if __name__ == '__main__':
    Directory = "Attenuation/"
    PdfPages = PdfPages('output_data/Attenuation' + '.pdf')
    targets = ["Al", "W", "Fe", "Mn", "Ni", "V", "Zr" ,"Be","pb","Cu"]
    x_offset = [1.55, 11, 7.3, 6.53, 8.5, 5.46, 2.3, 17.99]  # ,8.97]
    y_offset = [4500, 260, 400, 550, 330, 700, 3500, 100]  # ,275]
    n = [r'$\mathregular{K}^{\mathregular{Al}}$(1.55  KeV)',
         r'$\mathregular{L}^{\mathregular{W}}_{I,II,III}$(10.21,11.54,12.1 KeV)',
         r'$\mathregular{K}^{\mathregular{Fe}}$(7.11 KeV)',
         r'$\mathregular{K}^{\mathregular{Mn}}$(6.53  KeV)',
         r'$\mathregular{K}^{\mathregular{Ni}}$(8.33 KeV)',
         r'$\mathregular{K}^{\mathregular{V}}$(5.46 KeV)',
         r'$\mathregular{L}^{\mathregular{Zr}}_{I,II,III}$(2.22 ,2.30, 2.53 KeV)',
         r'$\mathregular{K}^{\mathregular{Zr}}$(17.9 KeV)']  # ,r'$\mathregular{K}^{\mathregular{Cu}}$(8.97 KeV)']
    scan =plotting.Attenuation()
    scan.attenuation_Energy(PdfPages=PdfPages, Directory=Directory,
                            targets=targets[0:3], x_offset=x_offset[0:3], y_offset=y_offset[0:3], n=n[0:3])
    scan.attenuation_thickness(PdfPages=PdfPages, Directory=Directory, targets =["Al"], logx = True, logy= True)
    scan.mass_attenuation_coeff(PdfPages=PdfPages, Directory=Directory, targets =targets)
    scan.close(PdfPages=PdfPages)
