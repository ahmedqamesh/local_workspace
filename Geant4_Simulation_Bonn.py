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
import csv
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

    def get_spectrum(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, save=True, Ratio=False, colors=False,
                     title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False, file=False, labels=False):
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
            if outputname == "RD53":
                loss1 = np.float(Entries[0] - Entries[1]) / np.float(Entries[0]) * 100
                ax.text(0.98, 0.70, "Intensity loss = %5.2f $\%%$ " % (loss1), horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), multialignment="left")
            else:
                loss1 = np.float(Entries[0] - Entries[1]) / np.float(Entries[0]) * 100
                loss2 = np.float(Entries[1] - Entries[2]) / np.float(Entries[1]) * 100
                loss3 = np.float(Entries[2] - Entries[3]) / np.float(Entries[2]) * 100
                ax.text(0.98, 0.70, "W/Be = %5.2f $\%%$ \n Be/Al = %5.2f $\%%$ \n Al/Chip = %5.2f $\%%$ " % (loss1, loss2, loss3), horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), multialignment="left")

        if title:
            ax.set_title(title)
        ax.set_xlabel(xtitle)
        ax.set_ylabel('Counts')
        ax.legend(loc="upper right")
        # ax.set_ylim(ymin=20)
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
                plt.savefig(Directory + location + "/gammaSpectrum_" + location + ".png", dpi=300)
            PdfPages.savefig()
        else:
            plt.show()

    def get_Secondary_spectrum(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, colors=False, table=False,
                               title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False):
        for i in range(len(test)):
            fig = plt.figure()
            gs = gridspec.GridSpec(2, 1, height_ratios=[3.5, 0.5])
            ax = plt.subplot(gs[0])
            ax2 = plt.subplot(gs[1])
            Entries = []
            file = Directory + location + "/gammaSpectrum_" + test[i] + ".root"
            f = ROOT.TFile(file)
            for j in range(len(hist_id)):
                t = f.Get(hist_id[j])
                Entries = np.append(Entries, t.GetEntries())
                data, x = self.readHistogram(file, t, False)
                entries = np.nonzero(data)
                ax.errorbar(x[:], data[:], fmt='-', color=colors[j], markersize=2, label=t.GetTitle())
                binmax = t.GetMaximumBin()
                binmin = t.GetMinimumBin()
                xmax = t.GetXaxis().GetBinCenter(binmax)
                xmin = t.GetXaxis().GetBinCenter(binmin)
                print t.GetEntries(), hist_id[j], t.GetTitle(), test[i]
            sum = Entries[0]  # np.sum(n)
            r = np.divide(Entries, sum) * 100  # this will give the ratio between each histogram to the total
            ax.set_xlabel(xtitle)
            ax.set_ylabel('Counts')
            ax.legend()
            ax.grid(True)
            ax.legend(loc="upper right")
            ax.set_title(r'Secondary charged particles produced ' + title[i], fontsize=11)
            ax2.set_axis_off()
            if logx:
                ax.set_xscale("log")
            if logy:
                ax.set_yscale("log")
            ax.set_xlim(xmin=0.01, xmax=30.0)
            columns = ('All secondary $e^-$', 'Transmitted secondaries $e^-$', 'Secondary Photo $e^-$', "Secondary Compton $e^-$")
            rows = ['Energy[KeV]', "Percentage [$\%$]"]
            data = [["$0-30$", "$< 1$", "$<1$", "$-$"], np.round(r, 3)]

            if table:
                ax2.table(cellText=data,
                          rowLabels=rows,
                          colWidths=[0.25 for x in columns],
                          colLabels=columns, cellLoc='center', rowLoc='center', loc='center', fontsize=14)
            plt.subplots_adjust(bottom=0.05)
            if outputname:
                plt.savefig(Directory + location + "/" + outputname + test[i] + ".png", dpi=300)
            else:
                plt.savefig(Directory + "/gammaSpectrum_" + test[i] + ".png", dpi=300)
            plt.tight_layout()
            PdfPages.savefig()

    def get_track_length(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, colors=False,
                         title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False):
        fig = plt.figure()
        gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])
        ax = plt.subplot(gs[0])
        ax1 = plt.subplot(gs[1])
        ax2 = plt.subplot(gs[2])

        def autolabel(rects, total):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rects:
                height = rect.get_height()
                ax1.text(rect.get_x() + rect.get_width() / 2., 250 + height, '%.1f $\%%$' % (height / total * 100), ha='center', va='top', fontsize=6, rotation=0)

        for k in range(len(test)):
            file = Directory + location + "/gammaSpectrum_" + test[k] + ".root"
            f = ROOT.TFile(file)
            for j in range(len(hist_id)):
                t = f.Get(hist_id[j])
                data, x = self.readHistogram(file, t, False)
                entries = np.nonzero(data)
                print t.GetEntries(), hist_id[j], test[k]
                if j == 0:
                    ax.errorbar(x[:], data[:], fmt='-', color=colors[j], markersize=2, label=t.GetTitle())
                    ax.set_title(title)
                    ax.set_xlabel(xtitle)
                    ax.set_ylabel('Counts')
                    ax.legend()
                    ax.grid(True)
                    if logx:
                        ax.set_xscale("log")
                    if logy:
                        ax.set_yscale("log")
                # Get vertex position
                if j == 1:
                    #ax1.errorbar(x[:], data[:], fmt='-', color=colors[j], markersize=2, label=t.GetTitle())

                    #ax1.set_title(r'Energy loss of 50 keV x rays through Layers', fontsize=11)
                    ax1.set_ylabel("Edep [ev]")
                    ax1.set_xlabel("Layer No.")

                    ax1.grid(True)
                    if logy:
                        ax.set_yscale("log")

        # Energy deposition from Geant4
        total_metal = []
        Edep = []
        thickness_nano = []
        with open(Directory + location + "/Energy_deposition.csv", 'r')as data:  # Get Data for the first Voltage
            reader = csv.reader(data)
            reader.next()
            for row in reader:
                total_metal = np.append(total_metal, str(row[0]))
                Edep = np.append(Edep, float(row[1]))
                thickness_nano = np.append(thickness_nano, float(row[2]))
        total_deposition = np.sum(Edep)
        Si_rho = 2.32  # g/cm3
        Cu_rho = 8.96  # g/cm3
        Al_rho = 2.70  # g/cm3
        Energy_range = ['4 Kev', '6 Kev', '10 Kev', '30 Kev', '50 Kev']
        Attenuation_Al = [3.605E+02, 1.153E+02, 2.621E+01, 1.128E+00, 3.681E-01]  # ['4 Kev','6 Kev','10 Kev','30 Kev','50 Kev',]
        Attenuation_Sio2 = [4.528E+02, 1.470E+02, 3.289E+01, 1.436, 4.385E-01]
        Attenuation_cu = [3.473E+02, 1.156E+02, 2.160E+02, 1.091E+01, 2.613]
        # Al_thickness = [2800] # nano 2.8
        # Cu_thickness = [3400,900,220*6,180] #nano 5.8
        # Si_thickness = [1000,800,670*2,175*6,310] #nano 4.5
        thickness_micro = [x * 1E-03 for x in thickness_nano]  # Micro  *1E-03
        thickness_cm = [x * 1E-07 for x in thickness_nano]  # cm *1E-07

        for E in np.arange(len(Energy_range)):
            y = []
            new_x = []
            att = []
            a = 0
            f = 1
            y_pos = np.arange(len(total_metal))
            # Get the depth as a distance from the first layer
            for l in y_pos:
                new_x = np.append(new_x, round(a, 2))
                a = a + thickness_micro[l]
            y = np.append(y, f)
            for i in np.arange(len(thickness_cm)):
                if total_metal[i] == "Al":
                    att = np.append(att, float(np.exp(- Attenuation_Al[E] * Si_rho * thickness_cm[i])))
                    if E == 0:
                        Al = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[1])
                        rect1 = ax1.bar(i, Edep[i] * 7, color=colors[1], align='center', alpha=0.5)  # Edep[i]*7 7: is just an enlargment factor to show a clearer bar
                        autolabel(rect1, total_deposition)

                if total_metal[i] == "cu":
                    att = np.append(att, float(np.exp(- Attenuation_cu[E] * Cu_rho * thickness_cm[i])))
                    if E == 0:
                        cu = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[2])
                        rect2 = ax1.bar(i, Edep[i], color=colors[2], align='center', alpha=0.5)
                        autolabel(rect2, total_deposition)

                if total_metal[i] == "sio2":
                    if i < 20:
                        att = np.append(att, float(np.exp(- Attenuation_Sio2[E] * Si_rho * thickness_cm[i])))
                    else:
                        new_x = np.append(new_x, new_x[i] + thickness_micro[-1])
                        att = np.append(att, float(np.exp(- Attenuation_Sio2[E] * Si_rho * thickness_cm[i])))
                    if E == 0:
                        sio2 = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[0])
                        rect3 = ax1.bar(i, Edep[i] * 7, color=colors[0], align='center', alpha=0.5)
                        autolabel(rect3, total_deposition)

                f = f * att[i]
                y = np.append(y, f)
            Energy = ax2.plot(new_x, y, ':', color=colors[E + 3], linestyle='dashed', label=Energy_range[E])
        ax1.set_title("Energy deposition of 50 keV x rays through Layers")
        #y_pos = np.arange(len(total_metal))
        ax1.set_ylim(0, Edep.max() + 600)
        ax2.get_xaxis().set_visible(False)
        ax1.legend(handles=[Al, cu, sio2], labels=["Al", "cu", "sio2"], loc="upper right")
        ax2.legend(loc="upper right", prop={'size': 6})
        ax2.set_xlabel('Layer Thickness ($\mu m $)')
        ax2.set_ylabel('Transmission $I$/$I_0$ ')
        # ax2.grid(True)
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
    Directory = "Simulation/"
    colors = ['red', '#006381', 'orange', '#33D1FF', 'green', 'black', 'grey', '#7e0044', 'black', "maroon", "yellow", "magenta"]
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

    energy = ["10keV", "20keV", "30keV", "40keV", "50keV"]
    models = ["emlivermore", "empenelope"]  # , "emstandardopt4"]
    spectrum = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "Al-0.15mm-Spectrum", "RD53"]
    RD53_layers = ["RD53-No", "RD53"]
    filters = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "Al-150um-Spectrum", "Fe-150um-Spectrum", "Mn-150um-Spectrum", "Zr-150um-Spectrum", "Ni-150um-Spectrum", "V-150um-Spectrum"]
    filters_machine = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "Al-150um-Spectrum"]  # ,"Zr-75um-Spectrum"]#, "Mn-25um-Spectrum", "Fe-15um-Spectrum" ,"Ni-15um-Spectrum","V-15um-Spectrum"]
    PdfPages = PdfPages('output_data/SimulationCurve_Bonn' + '.pdf')
    scan = Simulation()
    Geant4_empenelope_Diffenergys = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=energy, hist_id=["h3", "h3", "h3", "h3", "h3", "h3"], labels=energy,
                                                      logy=True, colors=colors, location="Geant4_empenelope_DiffEnergys", title=False)
    Geant4_DiffModels = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=models, hist_id=["h3", "h3", "h3"], labels=models, colors=colors,
                                          logy=True, outputname="DiffModels", location="Geant4_DiffModels", title=False)
    Geant4_RD53 = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=spectrum, hist_id=["28", "32", "32", "32"], labels=spectrum,
                                    logy=True, Ratio=True, colors=colors, location="RD53", outputname="spectrum", title="Tungsten x-ray spectrum x-ray spectrum ")
    Geant4_Filters = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=filters, hist_id=["28", "32", "32", "32", "32", "32", "32", "32", "32", "32"], labels=filters,
                                       logy=True, Ratio=False, location="Geant4_Filters", colors=colors,
                                       outputname="Diff_filters", title="Tungsten x-ray spectrum After Different Filters")
    Geant4_Filters = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=filters_machine, hist_id=["28", "32", "32", "32", "32", "32", "32", "32"], labels=filters_machine,
                                       logy=True, Ratio=False, location="machine_filters", colors=colors, outputname="machine_filters", title=False)
    RD53 = scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=RD53_layers, hist_id=["32", "32"], outputname="RD53", Ratio=True, colors=colors,
                             labels=["Without metal layers", "With metal layers"], logy=True, location="RD53", title="Tungsten Spectrum on the last layer of RD53 module")
    Secondary_electrons = scan.get_Secondary_spectrum(Directory=Directory, PdfPages=PdfPages, test=RD53_layers, table=True,
                                                      hist_id=["35", "37", "41", "42"], location="RD53", logy=True, logx=False, colors=colors,
                                                      outputname="Secondary_electrons", title=["with metal layers", "without metal layers"])
    tracklength = scan.get_track_length(Directory=Directory, PdfPages=PdfPages, test=["RD53"], hist_id=["39", "40"], location="RD53", logx=True, logy=True, colors=colors,
                                        title="Secondary electrons produced in the Metal Layers",
                                        outputname="Secondary_electrons_depth", xtitle="distance[mm]")
    scan.close()
