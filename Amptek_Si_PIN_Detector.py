from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import csv
from matplotlib import gridspec
from scipy.optimize import curve_fit
class Amptel_Spectrum():
    def linear(self, x, m, c):
        return m * x + c
    def red_chisquare(self, observed, expected, observed_error, popt):
        return np.sum(((observed - expected) / observed_error)**2 / (len(observed_error) - len(popt) - 1))

    def channel_energy_calibration(self, Directory=False, PdfPages=False):
        data = loadtxt(Directory+'Energy_channel_calibration/channel_energy_calibration_full_range.txt')
        x = data[:, 0]
        y = data[:, 1]
        x_offset = np.array([x[0]-119, x[1]-130, x[2]-140, x[3]-150, x[4]-170])
        y_offset = np.array([y[0]+1.3, y[1]+1.5, y[2]+1.6, y[3]+0.9, y[4]+1.5])
        n=[r'$Fe\ K_{I}$','$Fe\ K_{II}$', r'$Cd\ K_{I}$',r'$Cd\ K_{II}$', r'$Am\ {\gamma}_{2,0}$']
        
        plt.grid(True)
        # line fit
        line_fit, pcov = np.polyfit(x, y, 1, full=False, cov=True)
        fit_fn = np.poly1d(line_fit)
        line_fit_legend_entry = 'Line fit: ax+b\na=$%.5f\pm%.5f$\nb=$%.5f\pm%.5f$' % (line_fit[0], np.absolute(pcov[0][0]) ** 0.5, line_fit[1], np.absolute(pcov[1][1]) ** 0.5)
        line1, = plt.plot(np.arange(0, 1500), fit_fn(np.arange(0, 1500)), '-', color='darkgrey', label=line_fit_legend_entry)
        points1, = plt.plot(x, y, '.', color='black', label="Data")   
        for i, txt in enumerate(n):
            plt.text(x_offset[i], y_offset[i], txt, size=10)
        plt.legend()#handles=[points1, line1])
        ax = plt.gca()
        plt.xlim(0, 1600)
        plt.ylim(0, 70)
        plt.xlabel('Channel number')
        plt.ylabel('Energy / keV')
        plt.tight_layout()
        plt.savefig(Directory+"Energy_channel_calibration/channel_energy_calibration.png", bbox_inches='tight')
        PdfPages.savefig()
        
    def energy_spectrum(self, Directory=False, PdfPages=False,sources=False,real_time=False):
        color=['#1f77b4','#d62728','#7f7f7f','grey','#006381','#7e0044','black','red','#33D1FF',"maroon","yellow", "magenta",'lightblue']
        color2=['lightblue' ,'#F5A9BC','lightgrey','grey','#006381','#7e0044','black','red','#33D1FF',"maroon","yellow", "magenta",'lightblue']
        # energy calib E=a*x + b, x is the channel number
        a = 0.04258
        b = 0.09599
        for i in np.arange(len(sources)):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            data = loadtxt(Directory +"Source_spectra/"+sources[i]+"/"+sources[i]+"_spectrum_calibrated.txt")
            x1 = np.arange(0, len(data), 1)
            x_calib1 = a * x1 + b
            y1 = data
            y_rate1 = y1 / real_time[i] 
            y_norm1 = y1 / np.max(y1)
            am, = plt.step(x_calib1, y_norm1, where='mid', label=sources[i], linewidth=0.6, color=color[i], zorder=1.3)  # default farben 
            plt.bar(x_calib1, y_norm1, width=0.0425, linewidth=0.6, color=color2[i], zorder=1.2, label='_nolegend_')
            ax = plt.gca()
            if sources[i] =="Am":
                plt.xlim(0, 70)
            if sources[i] =="Fe":
                plt.xlim(0, 20)
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
    real_time=[60.715000,2148.976000 , 1.011000]  # Number is accumulation time
        
    PdfPages = PdfPages('output_data/Amptel_Spectrum' + '.pdf')
    scan = Amptel_Spectrum()
    scan.channel_energy_calibration(PdfPages=PdfPages, Directory=Directory)
    scan.energy_spectrum(PdfPages=PdfPages, Directory=Directory, sources =sources,real_time =real_time)
    
    scan.close()
    