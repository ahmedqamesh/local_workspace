from __future__ import division
import numpy as np
from scipy.optimize import curve_fit
import logging
loglevel = logging.getLogger('Analysis').getEffectiveLevel()
from analysis import logger
np.warnings.filterwarnings('ignore')
from analysis import analysis
from analysis import logger
import ROOT
from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1F, TFile, TH1D
from ROOT import gROOT, gBenchmark
import matplotlib.pyplot as plt

class Root_Utils(object):
    def __init__(self):
        self.log = logger.setup_derived_logger('Root')
        self.log.info('Root utils initialized')   
    
    def get_numpy_hist_from_root(self, fname, histname):
        # To call it
        # Directory = "/home/silab62/git/XrayMachine_Bonn/Calibration_Curves/Bonn/Simulation/"
        # root_files = [Directory+"Geant4/Geant4_empenelope_DiffEnergys/gammaSpectrum_10keV.root"]
        # Hist = get_numpy_hist_from_root(root_files[0],"h3")
        # print Hist
        rootfile = ROOT.TFile(fname)
        hist = rootfile.Get(histname)
        return hist2array(hist)

    def readHistogram(self, filename=None, histname=None, overflow=True):
        rootFile = TFile("file:%s" % filename)
    #        assert rootFile.IsOpen(), "could not open file %s" % filename
    #        try:
    #            rootHist = rootFile.Get(histname)
    #        except:
    #            raise
        
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


    def get_spectrum(self,Directory=False, PdfPages=False, test=False, hist_id=[0], location=False, save=True, Ratio=False, colors=False,
                     title=False, xtitle='Energy [keV]', outputname=False, logx=False, logy=False, file=False, labels=False, style=False, xmax=False, xmin=False):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        Entries = []
        for i in range(len(test)):
            file = Directory + location + "/gammaSpectrum_" + test[i] + ".root"
            f = ROOT.TFile(file)
            t = f.Get(hist_id[i])
            print (t.GetEntries(), hist_id[i], test[i])
            Entries = np.append(Entries, t.GetEntries())
            # t.Draw("t")
            data, x = self.readHistogram(filename=file, histname=t, overflow=False)
            entries = np.nonzero(data)
            if labels:
                label = labels[i]
            else:
                label = t.GetTitle()
            if style:
                style = style
            else:
                style = '-'
            ax.errorbar(x[:], data[:], fmt=style, color=colors[i], markersize=1, label=label)
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
        if xmax:
            ax.set_xlim(xmin=xmin, xmax=xmax)
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
        
        
    def getListOfHistograms(self, filename):
        rootFile = TFile("file:%s" % filename)
        assert rootFile.IsOpen(), "could not open file %s" % filename
        l = list(rootFile.GetListOfKeys())
        return [obj.GetName() for obj in l if obj.GetClassName() in __rootHistogramList__]

