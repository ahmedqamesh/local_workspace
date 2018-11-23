import sys
import os
import matplotlib
import ROOT
from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1F, TFile, TH1D
from ROOT import gROOT, gBenchmark
#import root_numpy as r2n
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import colors, cm
from matplotlib import pyplot as plt
#import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime as dt
import time
from pytz import timezone
from matplotlib import gridspec
from cProfile import label
matplotlib.rc('text', usetex=True)
params = {'text.latex.preamble': [r'\usepackage{siunitx}']}
plt.rcParams.update(params)


class Simulation():
    def makeExtent(self, xTicks, yTicks):
        dX = (xTicks[1] - xTicks[0]) / 2
        dY = (yTicks[1] - yTicks[0]) / 2
        return (yTicks[0] - dY, yTicks[-1] + dY, xTicks[0] - dX, xTicks[-1] + dX)

    def get_numpy_hist_from_root(self, fname, histname):

        rootfile = ROOT.TFile(fname)
        hist = rootfile.Get(histname)
        return hist2array(hist)
    # To call it
    # Directory = "/home/silab62/git/XrayMachine_Bonn/Calibration_Curves/Bonn/Simulation/"
    # root_files = [Directory+"Geant4/Geant4_empenelope_DiffEnergys/gammaSpectrum_10keV.root"]
    # Hist = get_numpy_hist_from_root(root_files[0],"h3")
    # print Hist

    def readHistogram(self, filename, histname, overflow=True):
        rootFile = TFile("file:%s" % filename)
        assert rootFile.IsOpen(), "could not open file %s" % filename
        try:
            rootHist = rootFile.Get(histname)
            #assert rootHist.Class().GetName() in __rootHistogramList__,"%s is not a histogram type"%rootHist.Class().GetName()
        except:
            raise
        rootHist = histname
        dims = int(rootHist.Class().GetName()[2])
        s = e = 1
        if overflow:
            s = 0
            e = 2

        if dims == 1:
            data = [rootHist.GetBinContent(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersX = [rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data), np.asarray(binCentersX)
        if dims == 2:

            data = [[rootHist.GetBinContent(j, i) for i in range(s, rootHist.GetNbinsY() + e)] for j in range(s, rootHist.GetNbinsX() + e)]
            binCentersX = [rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersY = [rootHist.GetYaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsY() + e)]

            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data), np.asarray(binCentersX), np.asarray(binCentersY)
        if dims == 3:
            data = [[[rootHist.GetBinContent(k, j, i) for i in range(s, rootHist.GetNbinsZ() + e)] for j in range(s, rootHist.GetNbinsY() + e)] for k in range(s, rootHist.GetNbinsX() + e)]
            binCentersX = [rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersY = [rootHist.GetYaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsY() + e)]
            binCentersZ = [rootHist.GetZaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsZ() + e)]
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data), np.asarray(binCentersX), np.asarray(binCentersY), np.asarray(binCentersZ)

    __rootHistogramList__ = ["TH%d%s" % (__i__, __type__) for __i__ in range(1, 4) for __type__ in ['C', 'S', 'I', 'F', 'D']]

    def getListOfHistograms(self, filename):
        rootFile = TFile("file:%s" % filename)
        assert rootFile.IsOpen(), "could not open file %s" % filename
        l = list(rootFile.GetListOfKeys())
        return [obj.GetName() for obj in l if obj.GetClassName() in __rootHistogramList__]

    def get_spectrum(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, save=True, Ratio=False,
                     title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False, file=False, labels=False):
        colors = ['red', '#006381', '#33D1FF', 'green', 'orange', 'maroon', 'black']
        fig = plt.figure()
        ax = fig.add_subplot(111)
        Entries = []
        for i in range(len(test)):
            file = Directory + location + "/gammaSpectrum_" + test[i] + ".root"
            f = ROOT.TFile(file)
            t = f.Get(hist_id[i])
            print t.GetEntries(), hist_id[i], test[i]
            Entries = np.append(Entries, t.GetEntries())
            # t.Draw("t")
            data, x = self.readHistogram(file, t, False)
            entries = np.nonzero(data)
            if labels:
                label = labels[i]
            else:
                label = t.GetTitle()
            ax.errorbar(x[:], data[:], fmt='-', color=colors[i], markersize=2, label=label)
#             ax.fill_between(x[1:], 0, data[1:], facecolor=colors[i], interpolate=True)
        if Ratio:
            loss1 = np.float(Entries[0] - Entries[1]) / float(Entries[0])
            loss2 = np.float(Entries[1] - Entries[2]) / float(Entries[1])
            loss3 = np.float(Entries[2] - Entries[3]) / float(Entries[2])
            ax.text(0.98, 0.70, "Ratios : \n W/Be = $%5.2f$ \n Be/Al = $%5.2f$ \n Al/Chip = $%5.2f$ " % (loss1, loss2, loss3), horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), multialignment="left")
        if title:
            ax.set_title(title)
        ax.set_xlabel(xtitle)
        ax.set_ylabel('Counts')
        ax.legend()
        ax.grid(True)
        if logx:
            ax.set_xscale("log")
        if logy:
            ax.set_yscale("log")
        plt.tight_layout()
        if save:
            if outputname:
                plt.savefig(Directory + location + "/gammaSpectrum_" + outputname + ".png", dpi=300)
            else:
                plt.savefig(Directory + "/gammaSpectrum_" + location + ".png", dpi=300)
            PdfPages.savefig()
        else:
            plt.show()

    def get_Secondary_spectrum(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, colors=False,
                               title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False):
        fig = plt.figure()
        gs = gridspec.GridSpec(2, 1, height_ratios=[3.5, 0.5])
        ax = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        n = []
        for i in range(len(test)):
            file = Directory + location + "/gammaSpectrum_" + test[i] + ".root"
            f = ROOT.TFile(file)
            for j in range(len(hist_id)):
                t = f.Get(hist_id[j])
                n = np.append(n, t.GetEntries())
                data, x = self.readHistogram(file, t, False)
                entries = np.nonzero(data)
                ax.errorbar(x[:], data[:], fmt='-', color=colors[j], markersize=2, label=t.GetTitle())
                print t.GetEntries(), hist_id[j], t.GetTitle()
        sum = np.sum(n)
        r = np.divide(n, sum) * 100
        ax.set_xlabel(xtitle)
        ax.set_ylabel('Counts')
        ax.legend()
        ax.grid(True)
        ax.legend(loc = "upper right")
        ax2.set_axis_off()
        if logx:
            ax.set_xscale("log")
        if logy:
            ax.set_yscale("log")
        ax.set_xlim(xmin=0.01,xmax=30.0)
        columns = ('Photo $e^-$', 'Compton $e^-$', 'AphotAuger or ComptAuger $e^-$', "PIXI Auger $e^-$")
        rows = ['Energy[KeV]', "Probability [%]"]
        data = [["$0-50$", "$< 10$", "$< 10$", "$< 10$"], np.round(r, 3)]
        ax2.table(cellText=data,
                  rowLabels=rows,
                  colWidths=[0.25 for x in columns],
                  colLabels=columns, cellLoc='center', rowLoc='center', loc='center', fontsize=16)
        plt.subplots_adjust(bottom=0.05)
        if outputname:
            plt.savefig(Directory + location + "/" + outputname + ".png", dpi=300)
        else:
            plt.savefig(Directory + "/gammaSpectrum_" + location + ".png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()

    def get_track_length(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False,
                           title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False):
        fig = plt.figure()
        gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1,1])
        ax = plt.subplot(gs[0])
        ax1 = plt.subplot(gs[1])
        ax2 = plt.subplot(gs[2])
        # Energy deposition from Geant4
        Energy_deposition = [16.612,88.628,26.367,2.3403 *1000 ,29.739,485.94,28.618,108.82,10.228, 106.49,9.9527,106.05,9.2885,103.3,9.9909,100.72,9.824,98.55,
                     8.4857,72.163,7.7287]# ev
        total_deposition =np.sum(Energy_deposition)
        Si_rho = 2.32 #g/cm3
        Cu_rho = 8.96 #g/cm3
        Al_rho = 2.70 #g/cm3
        
        Energy_range = ['50 Kev']
        Attenuation_Al = [1.128E+00, 5.684E-01,3.681E-01,2.778E-01]
        Attenuation_Sio2 = [0.859,0.463,0.318,0.252]
        Attenuation_cu = [1.119E-01,9.413E-02,8.363E-02,7.625E-02]
        Al_thickness = [2800] # nano 2.8
        Cu_thickness = [3400,900,220*6,180] #nano 5.8
        Si_thickness = [1000,800,670*2,175*6,310] #nano 4.5
        thickness_Micro =[x*1E-03 for x in [1000,2800,800,3400,670,900,670,220,175,220,175,220,175,220,175,220,175,220,175,180,310]] #Micro
        thickness = [x*1E-07 for x in [1000,2800,800,3400,670,900,670,220,175,220,175,220,175,220,175,220,175,220,175,180,310]] #cm
        total_Thickness = np.sum(thickness_Micro)
        total_metal = ["si02", "Al", "si02", "cu", "si02", "cu", "si02", "cu", "si02", "cu", "si02", "cu", "si02", "cu", "si02", "cu", "si02", "cu", "si02", "cu", "si02"]
        colors = ['red', '#006381', '#33D1FF', 'green', 'orange', 'maroon', 'black']
        for i in range(len(test)):
            file = Directory + location + "/gammaSpectrum_" + test[i] + ".root"
            f = ROOT.TFile(file)
            for j in range(len(hist_id)):
                t = f.Get(hist_id[j])
                data, x = self.readHistogram(file, t, False)
                entries = np.nonzero(data)
                if j == 0:
                    ax.errorbar(x[:], data[:], fmt='-', color=colors[j], markersize=2, label=t.GetTitle())    
                    ax.set_title(title)
                    ax.set_xlabel(xtitle)
                    ax.set_ylabel('Counts')
                    ax.legend()
                   # ax.set_xlim(0,3)
                    ax.grid(True)
                    if logx:
                        ax.set_xscale("log")
                    if logy:
                        ax.set_yscale("log")
                if j == 1:
                    ax1.errorbar(x[:], data[:], fmt='-', color=colors[j], markersize=2, label=t.GetTitle())
                    #ax1.set_xlim(2.85,3.45)
                    #ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x*10000)))
                    ax1.set_title("Vertex position")
                    ax1.set_xlabel(xtitle)
                    ax1.set_ylabel('Counts')
                    ax1.legend(loc = "upper right")
                    ax1.grid(True)
                     
        for E in np.arange(len(Energy_range)): 
            y=[]
            new_x = []
            att= []
            a =0 
            f = 1
            y_pos = np.arange(len(total_metal))
            # Get the depth as a distance from the first layer
            for i in y_pos:
                new_x = np.append(new_x,round(a, 2))
                a = a+thickness_Micro[i]
            y = np.append(y,f)    
            for i in np.arange(len(thickness_Micro)):    
                if total_metal[i] == "Al":
                    att = np.append(att,float(np.exp(- Attenuation_Al[E] * Si_rho* thickness[i])))
                    if E == 0 : 
                        Al = ax2.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[1])
                if total_metal[i] == "cu":
                    att = np.append(att,float(np.exp(- Attenuation_cu[E] * Cu_rho* thickness[i])))
                    if E == 0 : 
                        cu = ax2.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[2])
                if total_metal[i] == "si02": 
                    if i <20:
                        att = np.append(att,float(np.exp(- Attenuation_Sio2[E] * Si_rho* thickness[i])))
                    else:
                        new_x = np.append(new_x,new_x[i]+thickness_Micro[-1])
                        att = np.append(att,float(np.exp(- Attenuation_Sio2[E] * Si_rho* thickness[i])))
                    if E == 0 : 
                        sio2 = ax2.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[0])
                f = f*att[i]
                y = np.append(y,f)
            Energy = ax2.plot(new_x, y, ':',color=colors[E+3], linestyle='dashed', label =Energy_range[E])
        ax2.legend(handles =[Al,cu,sio2] , labels =["Al","cu", "sio2"])
        ax2.set_xlabel('Layer Thickness ($\mu m $)')
        ax2.set_ylabel('Transmission $I$/$I_0$ ')
        if outputname:
            plt.savefig(Directory + location + "/" + outputname + ".png", dpi=300)
        else:
            plt.savefig(Directory + "/gammaSpectrum_" + location + ".png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()

    def close(self):
        PdfPages.close()


if __name__ == '__main__':
    global PdfPages
    Directory = "Simulation/Geant4/"
    colors = ['green', 'black', 'orange', 'grey', '#006381', '#7e0044', 'black', 'red', '#33D1FF', "maroon", "yellow", "magenta"]
    x_offset = [10.21, 7.3, 1.55, 2.3, 6.53, 8.5, 5.46, 17.99, 8.97]
    y_offset = [4500000, 3000000, 430, 3500, 550, 330, 700, 100, 275]
    n = [r'$\mathregular{L}{\mathregular{W}}-{I,II,III}$(10.21,11.54,12.1 KeV)',
         r'$\mathregular{K}{\mathregular{Fe}}-{I,II}$(6 391, 7 11 KeV)',
         r'$\mathregular{K}^{\mathregular{Al}}$(1.55  KeV)',
         r'$\mathregular{L}^{\mathregular{Zr}}_{I,II,III}$(2.22 ,2.30, 2.53 KeV)',
         r'$\mathregular{K}^{\mathregular{Mn}}$(6.53  KeV)',
         r'$\mathregular{K}^{\mathregular{Ni}}$(8.33 KeV)',
         r'$\mathregular{K}^{\mathregular{V}}$(5.46 KeV)',
         r'$\mathregular{K}^{\mathregular{Zr}}$(17.9 KeV)',
         r'$\mathregular{K}^{\mathregular{Cu}}$(8.97 KeV)']

    energy = ["10keV", "20keV", "30keV", "40keV", "50keV", "60keV"]
    Filters = ["original", "Be", "Al", "Fe", "Mn", "Ni", "Va"]
    models = ["emlivermore", "empenelope", "emstandardopt4"]
    spectrum = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "Al-0.15mm-Spectrum", "RD53"]
    RD53_layers = ["RD53", "RD53_No"]
    Depth = ["with-metal-layers"]
    filters = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "Al-0.15mm-Spectrum", "Fe-0.15mm-Spectrum", "Mn-0.15mm-Spectrum", "Ni-0.15mm-Spectrum"]
    PdfPages = PdfPages('output_data/SimulationCurve_Bonn' + '.pdf')
    scan = Simulation()
    Geant4_empenelope_DiffEnergys = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=energy, hist_id=["h3", "h3", "h3", "h3", "h3", "h3"], labels=energy,
                                                      logy=True, location="Geant4_empenelope_DiffEnergys", title="Tungsten spectrum at different energies")
    Geant4_DiffModels = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=models, hist_id=["h3", "h3", "h3", "h3", "h3", "h3"], labels=models,
                                          logy=True, location="Geant4_DiffModels", title="Tungsten 50Kev Spectrum using Different Models")
    Geant4_Be_window = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=spectrum, hist_id=["28", "32", "32", "32"], labels=spectrum,
                                         logy=True, Ratio=True, location="Geant4_Be_window",
                                         outputname="spectrum", title="Tungsten 50 kev Spectrum")
    Geant4_Filters = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=filters, hist_id=["28", "32", "32", "32", "32", "32"], labels=filters,
                                       logy=True, Ratio=False, location="Geant4_Filters",
                                       outputname="Diff_filters", title="Tungsten Anode Spectrum After Different Filters")
    RD53 = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=RD53_layers, Ratio=False,
                             hist_id=["32", "32"], logy=True, location="RD53", title="Effect of metal layers on RD53")
    Secondary_electrons = scan.get_Secondary_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53"],
                                                      hist_id=["35","36","37","42"], location="RD53", logy=True,logx=False,colors=colors,
                                                      outputname="Secondary_electrons", title="Secondary electrons produced in the Metal Layers")
    tracklength =scan.get_track_length(Directory=Directory, PdfPages=PdfPages, test=["RD53"],hist_id=["43","44"],location="RD53",logx=False,logy=False,
                    title ="Secondary electrons produced in the Metal Layers",
                    outputname ="Secondary_electrons_depth",xtitle="distance[cm]")
    scan.close()
