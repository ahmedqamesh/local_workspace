import ROOT
from root_numpy import hist2array

def get_numpy_hist_from_root(fname, histname):

    rootfile = ROOT.TFile(fname)
    hist = rootfile.Get(histname)
    return hist2array(hist)




Directory = "/home/silab62/git/XrayMachine_Bonn/Calibration_Curves/Bonn/Simulation/"
root_files = [Directory+"Geant4/Geant4_empenelope_DiffEnergys/gammaSpectrum_10keV.root"]

Hist = get_numpy_hist_from_root(root_files[0],"h3")
print Hist 