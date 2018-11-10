import sys,os
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
import datetime as dt
import time
from pytz import timezone
from matplotlib import gridspec
matplotlib.rc('text', usetex = True)
params = {'text.latex.preamble': [r'\usepackage{siunitx}']}   
plt.rcParams.update(params)
class Simulation():
    def makeExtent(self, xTicks,yTicks):
       dX=(xTicks[1]-xTicks[0])/2
       dY=(yTicks[1]-yTicks[0])/2
       return (yTicks[0] -dY , yTicks[-1] + dY, xTicks[0] - dX, xTicks[-1]+ dX)
    def get_numpy_hist_from_root(self, fname, histname):
    
        rootfile = ROOT.TFile(fname)
        hist = rootfile.Get(histname)
        return hist2array(hist)
    # To call it 
    # Directory = "/home/silab62/git/XrayMachine_Bonn/Calibration_Curves/Bonn/Simulation/"
    # root_files = [Directory+"Geant4/Geant4_empenelope_DiffEnergys/gammaSpectrum_10keV.root"]
    # Hist = get_numpy_hist_from_root(root_files[0],"h3")
    # print Hist 

    def readHistogram(self,filename,histname,overflow=True):
        rootFile=TFile("file:%s"%filename)
        assert rootFile.IsOpen(),"could not open file %s"%filename
        try:
            rootHist=rootFile.Get(histname)
            #assert rootHist.Class().GetName() in __rootHistogramList__,"%s is not a histogram type"%rootHist.Class().GetName()
        except:
            raise
        rootHist=histname
        dims=int(rootHist.Class().GetName()[2])
        s = e = 1
        if overflow:
            s = 0
            e = 2
    
        if dims==1:
            data= [rootHist.GetBinContent(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersX=[rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data),np.asarray(binCentersX)
        if dims==2:
    
            data = [[rootHist.GetBinContent(j,i) for i in range(s, rootHist.GetNbinsY() + e)] for j in range(s, rootHist.GetNbinsX() + e) ]
            binCentersX = [rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersY = [rootHist.GetYaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsY() + e)]
    
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data),np.asarray(binCentersX),np.asarray(binCentersY)
        if dims==3:
            data = [[[rootHist.GetBinContent(k,j,i) for i in range(s, rootHist.GetNbinsZ() + e)] for j in range(s, rootHist.GetNbinsY() + e) ] for k in range(s, rootHist.GetNbinsX() + e) ]
            binCentersX = [rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersY = [rootHist.GetYaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsY() + e)]
            binCentersZ = [rootHist.GetZaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsZ() + e)]
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data),np.asarray(binCentersX),np.asarray(binCentersY),np.asarray(binCentersZ)
    
    __rootHistogramList__=["TH%d%s"%(__i__,__type__) for __i__ in range(1,4) for __type__ in ['C','S','I','F','D']]
    
    def getListOfHistograms(self,filename):
        rootFile = TFile("file:%s" % filename)
        assert rootFile.IsOpen(), "could not open file %s" % filename
        l=list(rootFile.GetListOfKeys())
        return [obj.GetName() for obj in l if obj.GetClassName() in __rootHistogramList__]
    
    def get_spectrum(self, Directory=False, PdfPages=False, test= False,hist_id=[0],location=False,
                     title=False,xtitle='Energy [keV]',outputname =False,logx=False,logy=False):
        colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon','black']
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(test)):
            file = Directory+location+"/gammaSpectrum_"+test[i]+".root"
            f = ROOT.TFile(file)
            t=f.Get(hist_id[i])
            #t.Draw("t")
            data,x=self.readHistogram(file,t, False)
            entries = np.nonzero(data)
            ax.errorbar(x[1:], data[1:], fmt='-',color = colors[i],markersize = 2, label =t.GetTitle())
            #ax.fill_between(x[1:], 0, data[1:], facecolor=colors[i], interpolate=True)
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
        if outputname :
            plt.savefig(Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_"+outputname+".png", dpi=300)
        else:
            plt.savefig(Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_"+location+".png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()
   
    def get_Secondary_spectrum(self, Directory=False, PdfPages=False, test= False,hist_id=[0],location=False,
                     title=False,xtitle='Energy [keV]',outputname =False,logx=False,logy=False):
        colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon','black']
        fig =plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(test)):
            file = Directory+location+"/gammaSpectrum_"+test[i]+".root"
            f = ROOT.TFile(file)
            for j in range(len(hist_id)):
                t=f.Get(hist_id[j])
                print t.GetEntries()
                data,x=self.readHistogram(file,t, False)
                entries = np.nonzero(data)
                ax.errorbar(x[:], data[:], fmt='-',color = colors[j],markersize = 2, label =t.GetTitle())
        #if title:
            #ax.set_title(title)
        ax.set_xlabel(xtitle)
        ax.set_ylabel('Counts')
        ax.legend()
        ax.grid(True)
        ax.set_xlim(xmin=0.0)
        #ax.set_ylim(ymin=0.0)
        ax.set_yscale("log")
        columns = ('Freeze', 'Wind', 'Flood')
        rows = ['%d year' % x for x in (100, 50)]
        data = [[ 66386, 174296,  75131],
                [ 58230, 381139,  78045]]
        plt.table(cellText=data,
                  rowLabels=rows,
                  colLabels=columns,
                  cellLoc = 'center', rowLoc = 'center',
                  loc='bottom')
        plt.subplots_adjust(left=0.2, bottom=0.2,wspace = 0.5,hspace = 0.3)
        if outputname :
            plt.savefig(Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_"+outputname+".png", dpi=300)
        else:
            plt.savefig(Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_"+location+".png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()
           
    def get_spectrum_depth(self, Directory=False, PdfPages=False, test= False,hist_id=[0],location=False,
                     title=False,xtitle='Energy [keV]',outputname =False,logx=False,logy=False):
        fig =plt.figure()
        gs = gridspec.GridSpec(2, 1, height_ratios=[2, 2])
        ax = plt.subplot(gs[0])
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        def autolabel(rects,total):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rects:
                height = rect.get_height()
                ax2.text(rect.get_x() + rect.get_width()/2., 1.05*height,'%.2f %%' % (height/total*100), ha='center', va='bottom')
        # Energy deposition from Geant4
        Energy_deposition = [70.3885,254.722,55.2842,1.98059*1000,42.7487,394.459,38.6216,82.0917,14.4346,82.8024,14.2578,
                             80.9561,13.9143,78.9877,13.6107, 76.8117,13.2364, 74.3392,12.557,54.8731,10.0689] # ev
        total_deposition =np.sum(Energy_deposition)
        Si_rho = 2.32 #g/cm3
        Cu_rho = 8.96 #g/cm3
        Al_rho = 2.70 #g/cm3
        Al_thickness = [2800] # nano 2.8
        Cu_thickness = [3400,900,220*6,180] #nano 5.8
        Si_thickness = [1000,800,670*2,175*6,310] #nano 4.5
        thickness = [x*1E-07 for x in [1000,2800,800,3400,670,900,670,220,175,220,175,220,175,220,175,220,175,220,175,180,310]] #cm
        total_Thickness =np.sum(thickness)
        total_metal = ["si02","Al","si02", "cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02"]
        colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon','black']
        for i in range(len(test)):
            file = Directory+location+"/gammaSpectrum_"+test[i]+".root"
            f = ROOT.TFile(file)
            t=f.Get(hist_id[i])
            data,x=self.readHistogram(file,t, False)
            entries = np.nonzero(data)
            ax1.errorbar(x[1:], data[1:], fmt='-',color = colors[i],markersize = 2, label =test[i] )
            #ax.fill_between(x[1:], 0, data[1:], facecolor=colors[i], interpolate=True)
        new_x = []
        layer_percent = []
        a =0 
        y_pos = np.arange(len(total_metal))
        # Get the depth as a distance from the first layer
        for i in y_pos:
            new_x = np.append(new_x,round(a, 2))
            a = a+thickness[i]
            layer_percent = np.append(layer_percent, (thickness[i]/total_Thickness)*100)  
        for i in np.arange(len(thickness)):    
            if total_metal[i] == "Al": 
                Al = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[1])
                rect1 = ax2.bar(i, Energy_deposition[i],color=colors[1], align='center', alpha=0.5)
                autolabel(rect1,total_deposition)
            if total_metal[i] == "cu":
                rect2 = ax2.bar(i, Energy_deposition[i],color=colors[2], align='center', alpha=0.5)
                cu = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[2])
                autolabel(rect2,total_deposition)
            if total_metal[i] == "si02": 
                new_x = np.append(new_x,new_x[i]+thickness[-1])
                sio2 = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[0])
                rect3 = ax2.bar(i, Energy_deposition[i],color=colors[0], align='center', alpha=0.5)
                autolabel(rect3,total_deposition)
        if title:
            ax.set_title(title)
        ax.set_xlabel(xtitle)
        ax.set_ylabel('Counts')
        ax.legend()
        ax.grid(True)
        #ax.set_xscale("log")
        #ax1.set_xscale("log")
        #ax.set_yscale("log")
        if outputname :
            plt.savefig(Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_"+outputname+".png", dpi=300)
        else:
            plt.savefig(Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_"+location+".png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()


    def filters(self, Directory=False, PdfPages=False,Filters=False,title ="Tungsten Anode Spectrum After Different Filters",
                hist_id=False,filter_thickness=False,xtitle='Energy [keV]',log=False):
        fig = plt.figure()
        #FigureCanvas(fig)
        ax = fig.add_subplot(111)
            
        for i in range(len(Filters)):
            file = Directory+"/Geant4_Filters/Tungsten_Spectrum_"+Filters[i]+".root"
            f = ROOT.TFile(file)
            if Filters[i] == "Test":
                t=f.Get("27")
            else:
                t=f.Get(hist_id)
            #t.Draw("t")
            data,x=self.readHistogram(file,t, False)
            entries = np.nonzero(data)
            ax.errorbar(x[1:], data[1:], fmt='-',markersize = 2, label =filter_thickness[i]+" "+Filters[i] )
        ax.set_title(title)
        ax.set_xlabel(xtitle)
        ax.set_ylabel('Counts')
        ax.legend()
        ax.grid(True)
        if log:
            ax.set_yscale("log")
        plt.savefig(Directory+"/Geant4_Filters/Tungsten_Spectrum_DiffFilters.png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()
                
    def close(self):
        PdfPages.close()
        
        
if __name__ == '__main__':
    global PdfPages
    Directory = "Simulation/Geant4/"
    Energy = ["10keV","20keV","30keV","40keV","50keV","60keV"]
    Filters = ["spectrum","Al","Fe","Mn","Ni","Va"]
    Model = ["emlivermore","empenelope","emstandardopt4"]
    Be_window =["Before-Beryllium-window","After-Beryllium-window"]
    RD53_layers = ["with-metal-layers","without-metal-layers"]
    Depth=["with-metal-layers"]
    filter_thickness = ["","15$\mu m $","15$\mu m $","15$\mu m $","15$\mu m $","15$\mu m $"]
    PdfPages = PdfPages('output_data/SimulationCurve_Bonn' + '.pdf')
    scan = Simulation()
    #scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=Energy,hist_id=["h3","h3","h3","h3","h3","h3"],log=True,location="Geant4_empenelope_DiffEnergys",title ="Tungsten spectrum at different energies")
    #scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=Model,hist_id=["h3","h3","h3","h3","h3","h3"],log=True,location="Geant4_DiffModels",title ="Tungsten 50Kev Spectrum using Different Models" )
    #scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=Be_window,hist_id=["27","32"],log=True,location="Geant4_Be_window",title ="Effect of Beryllium-window on 50Kev Spectrum")
    scan.get_spectrum(Directory=Directory, PdfPages=PdfPages, test=RD53_layers,
                      hist_id=["32","32"],logy=True,location="RD53",title ="Effect of metal layers on RD53")
    #scan.get_spectrum_depth(Directory=Directory, PdfPages=PdfPages, test=["with-metal-layers"],hist_id=["57"],location="RD53",logx=True,
    #                  title ="Secondary electrons produced in the Metal Layers",outputname ="Secondary electrons",xtitle="distance[cm]")
    scan.get_Secondary_spectrum(Directory=Directory, PdfPages=PdfPages, test=["with-metal-layers"],hist_id=["51","52","53","54"],location="RD53",logx=True,
                      title ="Secondary electrons produced in the Metal Layers",outputname ="Secondary electrons")
    #scan.filters(Directory=Directory, PdfPages=PdfPages,Filters=Filters,hist_id="32",log=True,filter_thickness=filter_thickness) 
    scan.close()