from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import csv
from matplotlib import gridspec

class Amptel_Spectrum():
    def energy_spectrum(self, Directory=False, PdfPages=False,sources=False,accumulation=False):
        color=['#1f77b4','#d62728','#7f7f7f','grey','#006381','#7e0044','black','red','#33D1FF',"maroon","yellow", "magenta",'lightblue']
        color2=['lightblue' ,'#F5A9BC','lightgrey','grey','#006381','#7e0044','black','red','#33D1FF',"maroon","yellow", "magenta",'lightblue']
        # energy calib E=a*x + b, x entspricht channel number
        a = 0.04258
        b = - 0.02886
        for i in np.arange(len(sources)):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            data = loadtxt(Directory +"Source_spectra/"+sources[i]+"/"+sources[i]+"_spectrum_calibrated.txt")
            x1 = np.arange(0, len(data), 1)
            x_calib1 = a * x1 + b
            y1 = data
            y_rate1 = y1 / accumulation[i] 
            y_norm1 = y1 / np.max(y1)
            am, = plt.step(x_calib1, y_norm1, where='mid', label=sources[i], linewidth=0.6, color=color[i], zorder=1.3)  # default farben 
            plt.bar(x_calib1, y_norm1, width=0.0425, linewidth=0.6, color=color2[i], zorder=1.2, label='_nolegend_')
            #am, = plt.step(x_calib1, y_norm1, where='mid', label='Data', linewidth=0.6, color='#B40431', zorder=1.3)  # layout wie bei spektren sonst
            #plt.bar(x_calib1, y_norm1, width=0.0425, linewidth=0.6, color='#F5A9BC', zorder=1.2, label='_nolegend_')  # layout wie bei spektren sonst
    
            # 
            # data2 = loadtxt('Tb_spectrum_calibrated.txt')
            # 
            # x2 = np.arange(0, len(data2), 1)
            # x_calib2 = a * x2 + b
            # y2 = data2
            # y_rate2 = y2 / 5506.972000  # zahl ist akkumulationszeit
            # y_norm2 = y2 / np.max(y2) # normiert auf maximalen Wert
            # tb, = plt.step(x_calib2, y_norm2, where='mid', label='Tb', linewidth=0.6, color='#ff7f0e', zorder=1.5)
            # plt.bar(x_calib2, y_norm2, width=0.0425, linewidth=0.6, color='#FFCC66', zorder=1.4, label='_nolegend_')
            # #tb, = plt.step(x_calib2, y_norm2, where='mid', label='Data', linewidth=0.6, color='#B40431', zorder=1.3)
            # #plt.bar(x_calib2, y_norm2, width=0.0425, linewidth=0.6, color='#F5A9BC', zorder=1.2, label='_nolegend_')
            # 
            # 
            # data3 = loadtxt('Ba_spectrum_calibrated.txt')
            # 
            # x3 = np.arange(0, len(data3), 1)
            # x_calib3 = a * x3 + b
            # y3 = data3
            # y_rate3 = y3 / 2633.494000  # zahl ist akkumulationszeit
            # y_norm3 = y3 / np.max(y3)
            # ba, = plt.step(x_calib3, y_norm3, where='mid', label='Ba', linewidth=0.6, color='#2ca02c', zorder=1.7)
            # plt.bar(x_calib3, y_norm3, width=0.0425, linewidth=0.6, color='lightgreen', zorder=1.6, label='_nolegend_')
            # #ba, = plt.step(x_calib3, y_norm3, where='mid', label='Data', linewidth=0.6, color='#B40431', zorder=1.3)
            # #plt.bar(x_calib3, y_norm3, width=0.0425, linewidth=0.6, color='#F5A9BC', zorder=1.2, label='_nolegend_')
            # 
            # 
            # 
            # data5 = loadtxt('Mo_spectrum_calibrated.txt')
            # 
            # x5 = np.arange(0, len(data5), 1)
            # x_calib5 = a * x5 + b
            # y5 = data5
            # y_rate5 = y5 / 495.949000 # zahl ist akkumulationszeit
            # y_norm5 = y5 / np.max(y5)
            # mo, = plt.step(x_calib5, y_norm5, where='mid', label='Mo', linewidth=0.6, color='#9900FF', zorder=1.84)
            # plt.bar(x_calib5, y_norm5, width=0.0425, linewidth=0.6, color='#CC99FF', zorder=1.82, label='_nolegend_')
            # #mo, = plt.step(x_calib5, y_norm5, where='mid', label='Data', linewidth=0.6, color='#B40431', zorder=1.3)
            # #plt.bar(x_calib5, y_norm5, width=0.0425, linewidth=0.6, color='#F5A9BC', zorder=1.2, label='_nolegend_')
            # 
            # 
            # data6 = loadtxt('Rb_spectrum_calibrated.txt')
            # 
            # x6 = np.arange(0, len(data6), 1)
            # x_calib6 = a * x6 + b
            # y6 = data6
            # y_rate6 = y6 / 1568.890000 # zahl ist akkumulationszeit
            # y_norm6 = y6 / np.max(y6)
            # rb, = plt.step(x_calib6, y_norm6, where='mid', label='Rb', linewidth=0.6, color='#8c564b', zorder=1.88)
            # plt.bar(x_calib6, y_norm6, width=0.0425, linewidth=0.6, color='#f3c16f', zorder=1.86, label='_nolegend_')
            # #rb, = plt.step(x_calib6, y_norm6, where='mid', label='Data', linewidth=0.6, color='#B40431', zorder=1.3)
            # #plt.bar(x_calib6, y_norm6, width=0.0425, linewidth=0.6, color='#F5A9BC', zorder=1.2, label='_nolegend_')
            # 
            # 
            # data7 = loadtxt('Cu_spectrum_calibrated.txt')
            # 
            # x7 = np.arange(0, len(data7), 1)
            # x_calib7 = a * x7 + b
            # y7 = data7
            # y_rate7 = y7 / 1540.534000 # zahl ist akkumulationszeit
            # y_norm7 = y7 / np.max(y7)
            # cu, = plt.step(x_calib7, y_norm7, where='mid', label='Cu', linewidth=0.6, color='#e377c2', zorder=1.92)
            # plt.bar(x_calib7, y_norm7, width=0.0425, linewidth=0.6, color='pink', zorder=1.9, label='_nolegend_')
            # #cu, = plt.step(x_calib7, y_norm7, where='mid', label='Data', linewidth=0.6, color='#B40431', zorder=1.3)
            # #plt.bar(x_calib7, y_norm7, width=0.0425, linewidth=0.6, color='#F5A9BC', zorder=1.2, label='_nolegend_')
            # 
            # 
            # 
            # #plt.plot(x, y, '-', color='black')
                
            ax = plt.gca()
            plt.xlim(0, 75)  # energy keV 0 bis 75 full range
            ax.set_ylim(bottom=0)
            plt.xlabel('Energy / keV')
            #plt.xlabel('Channel number')
            plt.ylabel('Counts (normalized)')
            #plt.legend(handles=[am,cd,fe]) #handles=[am, tb, ba, cd, mo, rb, cu, fe])
            #ax.set_xscale('log')
            #ax.set_yscale('log')
            ax.legend(loc='upper right')
            plt.tight_layout()
            plt.savefig(Directory+"Source_spectra/"+sources[i]+"/"+sources[i]+"_spectrum_calibrated", bbox_inches='tight')
            PdfPages.savefig()               
    def close(self):
        PdfPages.close()

if __name__ == '__main__':
    global PdfPages
    Directory = "Amptek_Si_PIN_Detector/"
    sources = ["Cd","Am","Fe"]
    accumulation=[1111.049000,1110.224000, 138.604000]  # Number is accumulation time
    x_offset = [1.55,10.21,2.3,7.3,6.53,8.5,5.46,17.99,8.97]
    y_offset = [4500,300,3500,430,550,330,700,100,275]
    n=[r'$\mathregular{K}^{\mathregular{Al}}$(1.55  KeV)',
       r'$\mathregular{L}^{\mathregular{W}}_{I,II,III}$(10.21,11.54,12.1 KeV)',
           r'$\mathregular{L}^{\mathregular{Zr}}_{I,II,III}$(2.22 ,2.30, 2.53 KeV)',
            r'$\mathregular{K}^{\mathregular{Fe}}$(7.11 KeV)',
            r'$\mathregular{K}^{\mathregular{Mn}}$(6.53  KeV)',
            r'$\mathregular{K}^{\mathregular{Ni}}$(8.33 KeV)',
             r'$\mathregular{K}^{\mathregular{V}}$(5.46 KeV)',
              r'$\mathregular{K}^{\mathregular{Zr}}$(17.9 KeV)',
              r'$\mathregular{K}^{\mathregular{Cu}}$(8.97 KeV)']
        
    PdfPages = PdfPages('output_data/Amptel_Spectrum' + '.pdf')
    scan = Amptel_Spectrum()
    scan.energy_spectrum(PdfPages=PdfPages, Directory=Directory, sources =sources,accumulation =accumulation)
    
    scan.close()
    