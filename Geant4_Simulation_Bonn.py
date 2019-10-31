
from analysis import plotting
from analysis import analysis
from analysis import root_utils

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import colors, cm
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.ticker as ticker
import datetime as dt
import time
import csv
from pytz import timezone
from matplotlib import gridspec
from cProfile import label
import sys
import os
import ROOT
from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1F, TFile, TH1D
from ROOT import gROOT, gBenchmark
import numpy as np
import logging

ro = root_utils.Root_Utils()

def makeExtent(xTicks, yTicks):
    dX = (xTicks[1] - xTicks[0]) / 2
    dY = (yTicks[1] - yTicks[0]) / 2
    return (yTicks[0] - dY, yTicks[-1] + dY, xTicks[0] - dX, xTicks[-1] + dX)

def Rd53_metal_layers(location=False, Directory=False, ax2=False):
    total_metal = []
    thickness_nano = []
    with open(Directory + location + "/Energy_deposition.csv", 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        reader.next()
        for row in reader:
            total_metal = np.append(total_metal, str(row[0]))
            thickness_nano = np.append(thickness_nano, float(row[2]))
    thickness_micro = [x * 1E-03 for x in thickness_nano]  # nano to micro  *1E-03
    total_thickness = np.sum(thickness_micro)
    # Get the depth as a distance from the first layer
    new_x = []
    y_pos = np.arange(len(total_metal))
    a = 0
    for l in y_pos:
        new_x = np.append(new_x, round(a, 2))
        a = a + thickness_micro[l]
    y = []
    f = 1        
    y = np.append(y, f)  # fill the start point with 1 (100% intensity)
    for i in np.arange(len(total_metal)):
        att_exp = []
        if total_metal[i] == "Al":
            Al = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[1])
        if total_metal[i] == "cu":
            cu = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[2])
        if total_metal[i] == "sio2":
            if i >= 20:
                new_x = np.append(new_x, new_x[i] + thickness_micro[-1])
            sio2 = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[0])  
    return  total_thickness 


def get_attenuation(Directory=False, PdfPages=False, location=False, title=False, colors=colors):
    fig = plt.figure()
    ax2 = plt.subplot(111)
    # Energy deposition from Geant4
    total_metal = []
    Edep = []
    thickness_nano = []
    with open(Directory + location + "/Energy_deposition.csv", 'r')as data:  # Get Data for the first Voltage
        reader = csv.reader(data)
        next(reader)
        for row in reader:
            total_metal = np.append(total_metal, str(row[0]))
            thickness_nano = np.append(thickness_nano, float(row[2]))
    # Al_thickness = [2800] # nano 2.8um
    # Cu_thickness = [3400,900,220*6,180] #nano 5.8um
    # Si_thickness = [1000,800,670*2,175*6,310] #nano 4.5um
    Si_rho = 2.32  # g/cm3
    Cu_rho = 8.96  # g/cm3
    Al_rho = 2.70  # g/cm3
    Energy_range = ['4 Kev', '6 Kev', '10 Kev', '30 Kev', '50 Kev']
    Attenuation_Al = [3.605E+02, 1.153E+02, 2.621E+01, 1.128E+00, 3.681E-01]  # ['4 Kev','6 Kev','10 Kev','30 Kev','50 Kev',] decrease 
    Attenuation_Sio2 = [0.2678E+03, 0.8541E+02, 0.1910E+02, 0.8453E+00 , 0.3143E+00]  # [4.528E+02, 1.470E+02, 3.289E+01, 1.436, 4.385E-01]decrease 
    Attenuation_cu = [3.473E+02, 1.156E+02, 2.160E+02, 1.091E+01, 2.613]
    thickness_micro = [x * 1E-03 for x in thickness_nano]  # Micro  *1E-03
    thickness_cm = [x * 1E-07 for x in thickness_nano]  # cm *1E-07
    Total_thickness = np.sum(thickness_micro)
    points = 10
    for E in np.arange(len(Energy_range)):
        new_x = []
        att = []
        a = 0
        y = []
        f = 1
        xpos = []
        # Get the depth as a distance from the first layer
        for l in np.arange(len(total_metal)):
            new_x = np.append(new_x, round(a, 2))
            a = a + thickness_micro[l]
        y = np.append(y, f)  # fill the start point with 1 (100% intensity)
        for i in np.arange(len(thickness_cm)):
            att_exp = []
            if total_metal[i] == "Al":
                width_space = np.linspace(0, thickness_cm[i], points)
                x_exp = np.linspace(new_x[i], new_x[i + 1], points)    
                for w in width_space:
                    att_exp = np.append(att_exp, float(f * np.exp(-Attenuation_Al[E] * Al_rho * w)))
                att = np.append(att, float(np.exp(-Attenuation_Al[E] * Al_rho * thickness_cm[i])))
                ax2.plot(x_exp, att_exp, '-', color=colors[E + 3], markersize=1, linestyle='dashed')
                if E == 0:
                    Al = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[1])
            if total_metal[i] == "cu":
                width_space = np.linspace(0, thickness_cm[i], points)
                x_exp = np.linspace(new_x[i], new_x[i + 1], points)  
                for w in width_space:
                    att_exp = np.append(att_exp, float(f * np.exp(-Attenuation_cu[E] * Cu_rho * w)))
                att = np.append(att, float(np.exp(-Attenuation_cu[E] * Cu_rho * thickness_cm[i])))
                ax2.plot(x_exp, att_exp, '-', color=colors[E + 3], markersize=1, linestyle='dashed')
                if E == 0:
                    cu = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[2])
            if total_metal[i] == "sio2":
                width_space = np.linspace(0, thickness_cm[i], points)
                for w in width_space:
                    att_exp = np.append(att_exp, float(f * np.exp(-Attenuation_Sio2[E] * Si_rho * w)))
                att = np.append(att, float(np.exp(-Attenuation_Sio2[E] * Si_rho * thickness_cm[i])))
                if i < 20:
                    x_exp = np.linspace(new_x[i], new_x[i + 1], points)  
                else:
                    x_exp = np.linspace(new_x[i], new_x[i] + thickness_micro[-1], points)
                    new_x = np.append(new_x, new_x[i] + thickness_micro[-1])
                ax2.plot(x_exp, att_exp, '-', color=colors[E + 3], markersize=1, linestyle='dashed')
                if E == 0:
                    sio2 = ax2.axvspan(new_x[i], new_x[i + 1], alpha=0.5, color=colors[0])
            xpos = np.append(xpos, (new_x[i] + new_x[i + 1]) * 0.5)
            f = f * att[i]
            y = np.append(y, f)
        Energy = ax2.plot(new_x, y, 'o', color=colors[E + 3], label=Energy_range[E], markersize=1)  # , linestyle='dashed')
    ax2.set_title(title)
    x_pos = np.arange(0, len(total_metal))
    # ax2.set_xticks(xpos,x_pos.tolist())
    ax2.set_xlim(xmax=Total_thickness)
    plt.xticks([])
    ax2.legend(loc="upper right", prop={'size': 9})
    
    ax2.set_xlabel('Layer stack')
    ax2.set_ylabel('Transmission $I$/$I_0$ ')
    plt.savefig(Directory + location + "/gammaSpectrum_Attenuation" + location + ".png", dpi=300)
    PdfPages.savefig()

def get_Secondary_spectrum(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, colors=False, table=False, style="-",
                           title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False, xmax=False, xmin=False):
    for i in range(len(test)):
        fig = plt.figure()
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
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
            ax.errorbar(x[:], data[:], fmt=style, color=colors[j], markersize=1, label=t.GetTitle())
            binmax = t.GetMaximumBin()
            binmin = t.GetMinimumBin()
            # xmax = t.GetXaxis().GetBinCenter(binmax)
            # xmin = t.GetXaxis().GetBinCenter(binmin)
            # print t.GetEntries(), hist_id[j], t.GetTitle(), test[i]
        sum = Entries[0]  # np.sum(n)
        r = np.divide(Entries, sum) * 100  # this will give the ratio between each histogram to the total
        ax.set_xlabel(xtitle)
        ax.set_ylabel('Counts')
        ax.legend()
        ax.grid(True)
        ax.legend(loc="upper right")
        ax.set_title(r'Secondary charged particles produced ' + title[i], fontsize=11)
        if logx:
            ax.set_xscale("log")
        if logy:
            ax.set_yscale("log")
        if xmax: 
            ax.set_xlim(xmin=xmin, xmax=xmax)
        columns = ('All secondary $e^-$', 'Transmitted secondaries $e^-$', 'Secondary Photo $e^-$', "Secondary Compton $e^-$")
        rows = ['Energy[Kev]', "Percentage [$\%$]"]
        data = [["$0-30$", "$< 1$", "$<1$", "$-$"], np.round(r, 3)]
        if table:
            ax2.table(cellText=data,
                      rowLabels=rows,
                      colWidths=[0.25 for x in columns],
                      colLabels=columns, cellLoc='center', rowLoc='center', loc='center', fontsize=14)
        plt.subplots_adjust(bottom=0.05)
        ax2.set_axis_off()
        if outputname:
            plt.savefig(Directory + location + "/" + outputname + test[i] + ".png", dpi=300)
        else:
            plt.savefig(Directory + "/gammaSpectrum_" + test[i] + ".png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()


def Energy_deposition(self, Directory=False, PdfPages=False, hist_id=[0], test=False, labels=False, style='-', location=False, colors=False,
                      title=False, xtitle='Energy [keV]', outputname=False, xmax=False, xmin=False, logy=True):
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[2.8, 1.2])
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])

    def autolabel(rects, total):
        """
        Attach a text label above each bar displaying its height
        """
        for rect in rects:
            height = rect.get_height()
            ax2.text(rect.get_x() + rect.get_width() / 2., 800 + height, '%.1f $\%%$' % (height / total * 100), ha='center', va='top', fontsize=6, rotation=90)

    Entries = []
    for i in range(len(test)):
        file = Directory + location + "/gammaSpectrum_" + test[i] + ".root"
        print (file)
        f = ROOT.TFile(file)
        t = f.Get(hist_id[i])
        Entries = np.append(Entries, t.GetEntries())
        # t.Draw("t")
        data, x = self.readHistogram(file, t, False)
        entries = np.nonzero(data)
        if labels:
            label = labels[i]
        else:
            label = t.GetTitle()
        if style:
            style = style
        else:
            style = '-'
        if logy:
            ax1.set_yscale("log")
        ax1.errorbar(x[1:], data[1:], fmt=style, color=colors[i], markersize=1, label=label)
        print (t.GetEntries(), hist_id[i], test[i] , t.GetTitle())
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
    for i in np.arange(len(total_metal)):
        if total_metal[i] == "Al":
                rect1 = ax2.bar(i, Edep[i] * 10, color=colors[1], align='center', alpha=0.5)  # Edep[i]*7 7: is just an enlargment factor to show a clearer bar
                autolabel(rect1, total_deposition)
        if total_metal[i] == "cu":
                rect2 = ax2.bar(i, Edep[i], color=colors[2], align='center', alpha=0.5)
                autolabel(rect2, total_deposition)
        if total_metal[i] == "sio2":
                rect3 = ax2.bar(i, Edep[i] * 10, color=colors[0], align='center', alpha=0.5)
                autolabel(rect3, total_deposition)    
    if title:
        ax1.set_title(title)
    ax1.set_ylabel('Counts')
    ax1.set_xlabel('Energy[Kev]')
    ax1.set_xlim(xmin=0, xmax=50)
    y_pos = np.arange(1, len(total_metal))
    ax2.set_ylim(0, Edep.max() + 900)
    ax2.set_xticks(y_pos)
    ax2.legend(handles=[rect1, rect2, rect3], labels=["Al", "cu", "sio2"], loc="upper right", prop={'size': 7})
    ax1.legend(loc="upper right", prop={'size': 8}) 
    ax2.set_ylabel('Edep [kev]')
    ax2.set_xlabel('Layer Number')
    # ax2.grid(True)
    ax1.grid(True)
    if outputname:
        plt.savefig(Directory + location + "/" + outputname + ".png", dpi=300)
    else:
        plt.savefig(Directory + "/gammaSpectrum_" + location + ".png", dpi=300)
    plt.tight_layout()
    PdfPages.savefig()


def Metal_layers(self, Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, save=True, colors=False, xmax=False, xmin=False,
                 title=False, xtitle='Energy [keV]', outputname=False, style="-", logx=False, logy=False, file=False, labels=False):
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])
    Entries = []
    for i in range(len(test)):
        file = Directory + location + "/gammaSpectrum_" + test[i] + ".root"
        f = ROOT.TFile(file)
        t = f.Get(hist_id[i])
        print (t.GetEntries(), hist_id[i], test[i])
        Entries = np.append(Entries, t.GetEntries())
        # t.Draw("t")
        data, x = self.readHistogram(file, t, False)
        entries = np.nonzero(data)
        if labels:
            label = labels[i]
        else:
            label = t.GetTitle()
        ax1.errorbar(x[:] * 1000, data[:], fmt=style, color='black', markersize=0.5, label=label)
    total_thickness = self.Rd53_metal_layers(Directory=Directory, location=location, ax2=ax2)
    ax1.axvline(x=total_thickness, linewidth=0.5, color='#d62728', linestyle='dashed')
    ax1.set_title(title)
    # ax1.set_xticks(y_pos)
    ax1.set_ylabel('Counts')
    ax2.get_xaxis().set_visible(False)
    ax2.set_axis_off()
    ax1.set_xlabel(xtitle)
    if xmax:
        ax1.set_xlim(xmin=xmin, xmax=xmax)
        ax2.set_xlim(xmin=xmin, xmax=xmax)
    else:
        ax1.set_xlim(xmin=0.0, xmax=total_thickness)
        ax2.set_xlim(xmin=0.0, xmax=total_thickness)
    ax1.legend(loc="upper right", prop={'size': 8})
    
    if logx:
        ax1.set_xscale("log")
    if logy:
        ax1.set_yscale("log")   
    
    ax1.grid(True)
    plt.savefig(Directory + location + "/" + outputname + ".png", dpi=300)
    plt.tight_layout()
    PdfPages.savefig()

if __name__ == '__main__':
    
    global PdfPages
    Directory = "Simulation/"
    colors = ['red', '#006381', '#7e0044', 'grey', "magenta", "maroon", 'green', 'orange', '#33D1FF', 'black', '#7e0044', 'black', "yellow"]
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
    spectrum = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "RD53", "RD53"]
    RD53_layers = ["RD53-No", "RD53"]
    filters = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "Al-150um-Spectrum", "Fe-150um-Spectrum", "Mn-150um-Spectrum", "Zr-150um-Spectrum", "Ni-150um-Spectrum", "V-150um-Spectrum"]
    filters_machine = ["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "V-15um-Spectrum", "Ni-15um-Spectrum", "Fe-15um-Spectrum", "Mn-25um-Spectrum", "Al-150um-Spectrum", "Zr-75um-Spectrum"]
    PdfPages = PdfPages('output_data/SimulationCurve_Bonn' + '.pdf')
    
    # X ray machine Simulation
    #     Geant4_empenelope_Diffenergys = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=energy, hist_id=["h3", "h3", "h3", "h3", "h3", "h3"], labels=energy,
    #                                                       logy=True, colors=colors, location="Geant4_empenelope_DiffEnergys", title=False)
    #     Geant4_DiffModels = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=models, hist_id=["h3", "h3", "h3"], labels=models, colors=colors,
    #                                           logy=True, outputname="DiffModels", location="Geant4_DiffModels", title=False)
    #     Geant4_Filters = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=filters, hist_id=["28", "32", "32", "32", "32", "32", "32", "32", "32", "32"], labels=filters,
    #                                        logy=True, Ratio=False, location="Geant4_Filters", colors=colors,
    #                                        outputname="Diff_filters", title="Tungsten x-ray spectrum After Different Filters")
    #     Geant4_Filters = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=filters_machine, hist_id=["28", "32", "32", "32", "32", "32", "32", "32"], labels=filters_machine,
    #                                        logy=True, Ratio=False, location="machine_filters", colors=colors, outputname="machine_filters", title=False)
        
    # RD53 Simulation    
        # Attenuation = get_attenuation(Directory=Directory, PdfPages=PdfPages, location="RD53", title="Attenuation of photons through metal layer stack", colors=colors)
       # 
        # Energy_deposition = Energy_deposition(Directory=Directory, PdfPages=PdfPages, test=["RD53", "RD53", "RD53", "RD53"], logy=True, hist_id=["9", "7", "8", "2"], xmin=0.0, xmax=60, location="RD53", colors=colors,
        #                                           title=False,  # "Energy deposition of 50 keV endpoint X-rays through metal layer stack",
        #                                           labels=["Total Edep in Sio2 Layers", "Total Edep in Al Layers", "Total Edep in Cu Layers", "TotalEnergy Deposited"],
        #                                           outputname="Energy_deposition_depth", xtitle="distance[mm]")
    #     Geant4_RD53 = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=spectrum, hist_id=["28", "32", "23", "32"], labels=["Tungsten-Spectrum", "Be-0.3mm-Spectrum", "Al-0.15mm-Spectrum","RD53 Last Layer"],
    #                                     logy=True, Ratio=True, colors=colors, location="RD53", outputname="spectrum",
    #                                      title="Tungsten x-ray spectrum in the back of the last metal layer stack of RD53")
        
    RD53 = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=RD53_layers, hist_id=["32", "32"], outputname="RD53_Spectrum",
                             Ratio=False, colors=colors, labels=["Without metal layers", "With metal layers"], logy=True,
                              location="RD53", title="Tungsten x-ray spectrum in the back of the last metal layer stack of RD53")

    #     tracklength = Metal_layers(Directory=Directory, PdfPages=PdfPages, test=["RD53"], hist_id=["39"], location="RD53", logx=False, logy=True, style="-", colors=colors,xmin=0.0, xmax=800,
    #                                         title="Track length of charged secondaries",outputname="Secondary_electrons_depth", xtitle="Track Length [$\mu m $]")
    # 
    #     Vertex = Metal_layers(Directory=Directory, PdfPages=PdfPages, test=["RD53"], hist_id=["40"], location="RD53", colors=colors, style="--",
    #                                                title="x-vertex of charged secondaries in RD53",outputname="Vertex",xtitle="Vertex position [$\mu m $]")
    #     
    #     Secondary_electrons = get_Secondary_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53"], table=True,
    #                                                       hist_id=["35", "37", "41", "42"], location="RD53", logy=True, logx=False, colors=colors,
    #                                                       outputname="Secondary_electrons", title=["with metal layers"])
    
# Extra tests
    Sio2 = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53-sio2"], hist_id=["9"], outputname="RD53-SiO2", Ratio=False, colors=['black', '#7e0044'], style="-",
                             logx=False, logy=True, location="RD53", title="Energy deposition in all the silicon layers [$4.5 \mu m$] of RD53 Metal Stack")
    
    Geant4_RD53_siO2 = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53-sio2", "RD53-sio2"], hist_id=["23", "32"],
                                    logy=True, Ratio=False, colors=colors, location="RD53", outputname="spectrum_SiO2",
                                     title="Tungsten x-ray spectrum after [$4.5 \mu m$] $SiO_2$")

# Diode spectra
    Sio2_diode = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53-sio2-0.05"], hist_id=["9"], outputname="RD53-SiO2-0.05", Ratio=False, colors=['black', '#7e0044'], style="-",
                             logx=False, logy=True, location="RD53", title="Energy deposition in all the silicon layers [$50 \mu m$] of RD53 Metal Stack")
    
    Geant4_RD53_siO2_diode = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53-sio2-0.05", "RD53-sio2-0.05"], hist_id=["23", "32"],
                                    logy=True, Ratio=False, colors=colors, location="RD53", outputname="spectrum_SiO2_diode",
                                     title="Tungsten x-ray spectrum after [$50 \mu m$] $SiO_2$")

    G4_Cu = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53-G4-Cu"], hist_id=["8"], outputname="RD53-G4-Cu", Ratio=False, colors=['black', '#7e0044'], style="-",
                             logx=False, logy=True, location="RD53", title="Energy deposition in all the Copper layers [$5.8 \mu m$] of RD53 Metal Stack")
    
    Geant4_RD53_Cu = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53-G4-Cu", "RD53-G4-Cu"], hist_id=["23", "32"],
                                    logy=True, Ratio=False, colors=colors, location="RD53", outputname="spectrum_Cu",
                                     title="Tungsten x-ray spectrum after [$5.8 \mu m$] $Cu$")

#     Secondary_electrons = ro.get_Secondary_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53"], table=True,xmin=0.0, xmax=60,style="-",
#                                                       hist_id=["51", "52", "53", "54"], location="RD53", logy=True, logx=False, colors=colors,
#                                                       outputname="Secondary_electrons", title=["with metal layers"])
#     Radius = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53"], hist_id=["48"], outputname="radius", Ratio=False, colors=['black', '#7e0044'],style="-",xmin=0.0, xmax=0.02,
#                              logx=False, logy=False, location="RD53", title="Radius of secondary charged tracks at the last layer of RD53", xtitle="Radius[mm]")
#     
#     projection = ro.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=["RD53"], hist_id=["47"], outputname="radius", Ratio=False, colors=['black', '#7e0044'],style="-",
#                              logy=False, location="RD53", title="projected position of secondary charged tracks at the last layer of RD53", xtitle="Projected Position [mm]")
#          
    PdfPages.close()
