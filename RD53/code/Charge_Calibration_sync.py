from __future__ import division
from scipy.optimize import curve_fit
import logging
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit
from scipy import interpolate
import tables as tb
import numpy as np
import matplotlib.pyplot as plt
from bdaq53.analysis import analysis
from bdaq53.analysis import calibration_utils as cal
from bdaq53.analysis import plotting
from bdaq53.analysis import analysis_utils as au
import random
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
Directory = "/home/silab62/git/XrayMachine_Bonn/Charge_Calibration/sync/"
global PdfPages
PdfPages = PdfPages(Directory + 'Charge_calibration_sync.pdf')
scan_id = "charge_calibration"


def analyze(scan_id=scan_id, data_files=False, Interpreted_file=False, cols=[0], rows=[0], run_config=False, spline_file=False,
            titles=False, Directory=False):
    au.get_calibration_parameters_perpixel(Interpreted_file=Interpreted_file, Directory=Directory)
    # Creat Spline Calibration
    for i in range(len(data_files)):
        au.create_tdc_injection_calibration(scan_id=scan_id, data_file=data_files[i], run_config=run_config, chunk_size=80000, title=titles[i], cols=cols, rows=rows, spline_file=spline_file, Directory=Directory)


interpreted_file = [r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_sync/20181213_184614_hitor_calibration_interpreted.h5"]

source_files = [r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_sync/20181217_073435_source_scan_interpreted.h5", 
                "/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_sync/20181217_101456_source_scan_interpreted.h5"]
# Fit parameters are a1, a2, m1, m2, sd1, sd2

calibrated_fit_parameters = [(160000, 180, 5),
                             (1650, 1000, 610, 700, 10, 10)]  # Cd

calibrated_fit_ranges = [(130, 220),(580, 731)]

titles = ["Fe","Cd"]
peaks = []
peaks_error = []
sigmas = []
sigmas_error = []
selected_columns = range(0, 64)
selected_rows = range(0, 192)
spline_file = Directory + "UnivariateSpline.npy"
with tb.open_file(interpreted_file[0], 'r') as in_file:
    hist_tdc_mean = in_file.root.hist_tdc_mean[:]
    run_config = au.ConfigDict(in_file.root.configuration.run_config[:])
    scan_parameter_range = np.array([v - run_config['VCAL_MED'] for v in run_config['VCAL_HIGH_values']])
    #cal.distribution(Directory=Directory, Hist=in_file.root.Hits[:], PdfPages=PdfPages)
    data_Analysis = analyze(Interpreted_file=interpreted_file[0], data_files=source_files, cols=selected_columns,
                            rows=selected_rows, titles=titles, run_config=run_config, spline_file=spline_file, Directory=Directory)

with tb.open_file(Directory + 'h5_files/tdc_Calibrated_data_' + titles[0] + '.h5', 'r') as in_file:
    cluster_background = in_file.root.Cluster[:]

for i in np.arange(len(titles)):
    calibration_file = Directory + 'h5_files/tdc_Calibrated_data_' + titles[i] + '.h5'
    with plotting.Plotting(analyzed_data_file=calibration_file) as p:
        peak, peak_error, sigma, sigma_error = p.plot_tdc_gamma_spectrum(cols=selected_columns, rows=selected_rows, title=titles[i], calibrated_fit_parameters=calibrated_fit_parameters[i],
                                                                         calibrated_fit_ranges=calibrated_fit_ranges[i], cluster_background=cluster_background, background=True,
                                                                         PdfPages=PdfPages)
        peaks.extend(peak)
        peaks_error.extend(peak_error)
        sigmas.extend(sigma)
        sigmas_error.extend(sigma_error)
        #p.plot_deltavcal_tdc_hist(title='$\Delta$VCAL vs Tdc histogram (%s source)' % titles[i], PdfPages=PdfPages)
peaks = np.array(peaks[:])
peaks_error = np.array(peaks_error[:])
sigmas = np.array(sigmas[:])
sigmas_error = np.array(sigmas_error[:])
# # #     point_label_sel = [r'${K}_{\alpha}^{Fe}$', r'${K}_{\alpha,\beta}^{Cu}$', r'${K}_{\alpha}^{Nb}$', r'${K}_{\alpha}^{Mo}$', r'${K}_{\beta}^{Nb}$',
# # #                        r'${K}_{\alpha}^{Cd}$', r'${K}_{\beta}^{Cd}$']
# # #     peaks_sel = np.array([peaks[1], peaks[2], peaks[5], peaks[3], peaks[6], peaks[7], peaks[8]])
# # #     peaks_error_sel = np.array([peaks_error[1], peaks_error[2], peaks_error[5], peaks_error[3], peaks_error[6], peaks_error[7], peaks_error[8]])
# # #     sigmas_sel = np.array([sigmas[1], sigmas[2], sigmas[5], sigmas[3], sigmas[6], sigmas[7], sigmas[8]])
# # #     sigmas_error_sel = np.array([sigmas_error[1], sigmas_error[2], sigmas_error[5], sigmas_error[3], sigmas_error[6], sigmas_error[7], sigmas_error[8]])
# #     # Selected peaks
# #     x_sel = np.array([6.195, 8.48, 16.57, 17.427, 18.79, 22.075, 24.94])
# x_sel = np.array([6.195, 8.99, 17.775, 18.7125, 22.075, 24.94])
# point_label_sel = [r'${K}_{\alpha}^{Fe}$', r'${K}_{\alpha,\beta}^{Cu}$', r'${K}_{\alpha}^{Nb}$', r'${K}_{\alpha}^{Mo}$',
#                    r'${K}_{\alpha}^{Cd}$', r'${K}_{\beta}^{Cd}$']
# peaks_sel = np.array([peaks[1], peaks[2], peaks[3], peaks[4], peaks[5], peaks[6]])
# peaks_error_sel = np.array([peaks_error[1], peaks_error[2], peaks_error[3], peaks_error[4], peaks_error[5], peaks_error[6]])
# sigmas_sel = np.array([sigmas[1], sigmas[2], sigmas[3], sigmas[4], sigmas[5], sigmas[6]])
# sigmas_error_sel = np.array([sigmas_error[1], sigmas_error[2], sigmas_error[3], sigmas_error[5], sigmas_error[4], sigmas_error[6]])
# print peaks_sel
#
with plotting.Plotting(analyzed_data_file=Directory + 'h5_files/tdc_Calibrated_data_' + titles[0] + '.h5') as p:
    #     a, a_error, b, b_error = p.plot_vcal_energy_calibration(x=x_sel, y=peaks_sel, y_err=peaks_error_sel, point_label=point_label_sel, Directory=Directory, PdfPages=PdfPages)
    #     w = 3.65
    #     charge = x_sel / w * 1000
    #     charge_err = peaks_error_sel / w * 100
    #     p.plot_vcal_charge_calibration(x=peaks_sel, y=charge, y_err=charge_err, point_label=point_label_sel, Directory=Directory, PdfPages=PdfPages)
    #     p.plot_FWHM(x=x_sel, sigma=sigmas_sel, sigma_err=sigmas_error_sel, a=a, a_error=a_error, b=b, b_error=b_error, point_label=point_label_sel, Directory=Directory, PdfPages=PdfPages)
    p.create_Interpolation_perpixel(histogram=hist_tdc_mean, spline_file=spline_file, cols=selected_columns, rows=selected_rows,
                                    n_random_pixels=5, scan_parameter_range=scan_parameter_range, PdfPages=PdfPages)
    cal.plot_spline_masking(calibrated_file=Directory + 'h5_files/tdc_Calibrated_data_' + titles[0] + '.h5', PdfPages=PdfPages)
#
# Analyze a special source scan
# m = 0
# calibration_file = Directory + 'h5_files/tdc_Calibrated_data_' + titles[m] + '.h5'
# tests_title = ["tdc spectrum for " + titles[m] + " source"]
# with tb.open_file(calibration_file, 'r') as in_file:
#     cluster = in_file.root.Cluster[:]
#     cluster = cluster[cluster["range_status"] == 1]
#     tdc_data = cluster["tdc_value"]
# cal.source_test(PdfPages=PdfPages, Directory=Directory, tdc_data=tdc_data, tests_title="Cluster", ylabel=r"$\Delta$VCAL", scan_parameter_range=scan_parameter_range)
#  cal.plot_tdc_gamma_spectrum_kafe(cluster_hist=cluster, scan_parameter_range=scan_parameter_range, cols=selected_columns, title=titles[m], rows=selected_rows,
#                                   cluster_background=cluster_background, background=True,PdfPages=PdfPages)
# with plotting.Plotting(analyzed_data_file=source_files[m]) as p:
#     p.plot_tot_tdc_hist(title='Tot vs Tdc histogram for %s source' % titles[m], PdfPages=PdfPages)

PdfPages.close()
