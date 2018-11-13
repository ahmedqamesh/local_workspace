import irrad_spectroscopy as isp
import irrad_spectroscopy.spectroscopy as sp
import matplotlib.pyplot as plt
from irrad_spectroscopy.plot_utils import plot_spectrum
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import yaml

energy_cal = lambda x: 0.04258 * x - 0.02886  #energy calibration function

spectrum_cd_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Cd/Cd_spectrum_calibrated.txt'
spectrum_ba_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Ba/Ba_spectrum_calibrated.txt'
spectrum_am_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Am/Am_spectrum_calibrated.txt'
spectrum_fe_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Fe/Fe_spectrum_calibrated.txt'
spectrum_rb_file = '/home/silab62/git/XrayMachine_Bonn/Amptek_Si_PIN_Detector/Source_spectra/Rb/Rb_spectrum_calibrated.txt'

files = {'Am': spectrum_am_file, 'Fe': spectrum_fe_file, "Cd": spectrum_cd_file, 'Ba': spectrum_ba_file, 'Rb': spectrum_rb_file}
spectra = dict([(k, None) for k in files])

for f in files:
    spectra[f] = np.loadtxt(files[f])

peaks = dict([(k, None) for k in files])

for k in spectra:
    peaks[k], _ = sp.fit_spectrum(counts=spectra[k], n_peaks=1, xray=True, reliable=0)

energies = {'Cd': 22.075, 'Ba': 32.19, 'Am': 59.54, 'Fe': 5.89, 'Rb': 13.36}

peaks_fit = dict([(k, peaks[k]["peak_0"]) for k in peaks if k not in ['Cd', 'Rb', 'Ba']])
#print peaks_fit
calib = sp.do_energy_calibration(peaks_fit, energies)


am, bkg_am = sp.fit_spectrum(spectra['Am'], energy_cal=calib["func"], expected_accuracy=1e-3)
from irrad_spectroscopy.spec_utils import select_peaks
s_peaks = select_peaks(["Am"], am)
plot_spectrum(spectra['Am'], peaks=s_peaks, bkg=bkg_am, energy_cal=calib['func'])