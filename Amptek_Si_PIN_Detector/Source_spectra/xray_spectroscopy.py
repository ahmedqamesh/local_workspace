import irrad_spectroscopy as isp
import irrad_spectroscopy.spectroscopy as sp
import matplotlib.pyplot as plt
from irrad_spectroscopy.plot_utils import plot_spectrum
from matplotlib.backends.backend_pdf import PdfPages
from irrad_spectroscopy.spec_utils import select_peaks
import numpy as np
import yaml
from collections import OrderedDict
energy_cal = lambda x: 0.04258 * x - 0.02886  #energy calibration function
spectrum_cd_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Cd/Cd_spectrum_calibrated.txt'
spectrum_am_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Am/Am_spectrum_calibrated.txt'
spectrum_fe_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Fe/Fe_spectrum_calibrated.txt'
spectrum_bkg_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Background/Background_spectrum_calibrated.txt' 

files = {'Am': spectrum_am_file, 'Fe': spectrum_fe_file, 'Cd': spectrum_cd_file, 'Background':spectrum_bkg_file}
print files
spectra = dict([(k, None) for k in files])
for f in files:
    spectra[f] = np.loadtxt(files[f])

peaks = dict([(k, None) for k in files])
for k in spectra:
    peaks[k], _ = sp.fit_spectrum(counts=spectra[k],n_peaks=1,  xray=True, reliable=True)

energies = { 'Fe': 5.89, 'Fe': 6.49,'Cd': 22.075, 'Cd': 24.94, 'Am': 59.54}
peaks_fit = dict([(k, peaks[k]["peak_0"]) for k in peaks if k not in ['Background']])
calib = sp.do_energy_calibration(peaks_fit, energies)
# 
bkg_interpolate = sp.interpolate_bkg(spectra['Background'])

background, bkg_background = sp.fit_spectrum(spectra['Background'], bkg=bkg_interpolate , energy_cal=calib["func"],  xray=True, expected_accuracy=1e-2)
#s_peaks = select_peaks(["Background"], background)
plot_spectrum(spectra['Background'], peaks=background, bkg=bkg_background, energy_cal=calib['func'])