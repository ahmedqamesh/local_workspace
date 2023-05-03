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
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
Directory = "/home/silab62/git/Charge_Calibration/linear/50-50/"
global PdfPages
PdfPages = PdfPages(Directory + 'Charge_calibration_linear.pdf')
scan_id = "charge_calibration"


def analyze(scan_id=scan_id, data_files=False, Interpreted_file=False, cols=[0], rows=[0], run_config=False, spline_file=False,
            titles=False, Directory=False):
    # create Spline interpolation from hitor calibration
    au.get_calibration_parameters_perpixel(Interpreted_file=Interpreted_file, Directory=Directory)
    # Creat Spline Calibration per source
    for i in range(len(data_files)):
        au.create_tdc_injection_calibration(scan_id=scan_id, data_file=data_files[i], run_config=run_config, chunk_size=80000, title=titles[i], cols=cols, rows=rows, spline_file=spline_file, Directory=Directory)


interpreted_file = [r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190109_112623_hitor_calibration_interpreted.h5"]

# source_files = [r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_145728_source_scan_interpreted.h5",
#                 # r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190107_173237_source_scan_interpreted.h5",
#                 r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_192453_source_scan_interpreted.h5",  # Fe 7200
#                 r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_153240_source_scan_interpreted.h5",
#                 r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_142039_source_scan_interpreted.h5",
#                 r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_122634_source_scan_interpreted.h5",
#                 r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190107_150725_source_scan_interpreted.h5",
#                 r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_133857_source_scan_interpreted.h5"]

source_files = [r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/Newscan/20190123_160653_source_scan_interpreted.h5",
                # r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190107_173237_source_scan_interpreted.h5",
                r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_192453_source_scan_interpreted.h5",  # Fe 7200
                r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190108_153240_source_scan_interpreted.h5",
                r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/Newscan/20190123_183423_source_scan_interpreted.h5",  # Nb
                r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/Newscan/20190123_172508_source_scan_interpreted.h5",  # Mo
                r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/20190107_150725_source_scan_interpreted.h5",
                r"/media/silab62/e799a8d8-915c-4baf-9300-6ce63932dbc2/home/silab/RD53/interpreted_files_linear/50-50/0x0A4A/Newscan/20190123_145529_source_scan_interpreted.h5"]  # Sn

# Fit parameters are a1, a2, m1, m2, sd1, sd2
calibrated_fit_parameters = [(25000, 270, 5),  # Background
                             (160000, 190, 5),  # Fe
                             (200000, 270, 5),  # Cu
                             (100000, 30000, 510, 580, 10, 10),  # Nb
                             (90000, 30000, 530, 610, 10, 10),  # Mo
                             (1650, 1000, 650, 740, 10, 10),  # Cd
                             (14000, 2000, 780, 870, 10, 10)]  # Sn
calibrated_fit_ranges = [(170, 300),
                         (130, 220),
                         (230, 310),
                         (512, 600),
                         (530, 610),
                         (620, 760),
                         (660, 885)]
titles = ["Background", "Fe", "Cu", "Nb", "Mo", "Cd", "Sn"]
selected_columns = range(128, 264)
selected_rows = range(0, 192)
spline_file = Directory + "UnivariateSpline.npy"
with tb.open_file(interpreted_file[0], 'r') as in_file:
    hist_tdc_mean = in_file.root.hist_tdc_mean[:]
    run_config = au.ConfigDict(in_file.root.configuration.run_config[:])
    scan_parameter_range = np.array([v - run_config['VCAL_MED'] for v in run_config['VCAL_HIGH_values']])
    #cal.distribution(Directory=Directory, Hist=in_file.root.Hits[:], PdfPages=PdfPages)
#     data_Analysis = analyze(Interpreted_file=interpreted_file[0], data_files=source_files, cols=selected_columns,
#                             rows=selected_rows, titles=titles, run_config=run_config, spline_file=spline_file, Directory=Directory)
with tb.open_file(Directory + 'h5_files/tdc_Calibrated_data_' + titles[0] + '.h5', 'r') as in_file:
    cluster_background = in_file.root.Cluster[:]

peaks = []
peaks_error = []
sigmas = []
sigmas_error = []
for i in np.arange(len(titles)):
    calibration_file = Directory + 'h5_files/tdc_Calibrated_data_' + titles[i] + '.h5'
    with plotting.Plotting(analyzed_data_file=calibration_file) as p:
        peak, peak_error, sigma, sigma_error = p.plot_tdc_gamma_spectrum(cols=selected_columns, rows=selected_rows, title=titles[i], calibrated_fit_parameters=calibrated_fit_parameters[i],
                                                                         calibrated_fit_ranges=calibrated_fit_ranges[i], cluster_background=cluster_background, background=True,
                                                                         Normalise=False, PdfPages=PdfPages)
        peaks.extend(peak)
        peaks_error.extend(peak_error)
        sigmas.extend(sigma)
        sigmas_error.extend(sigma_error)
 #      p.plot_deltavcal_tdc_hist(title='$\Delta$VCAL vs Tdc histogram (%s source)' % titles[i], PdfPages=PdfPages)
peaks = np.array(peaks[:])
peaks_error = np.array(peaks_error[:])
sigmas = np.array(sigmas[:])
sigmas_error = np.array(sigmas_error[:])
x = [0, 6.195, 8.48, 16.57, 18.79, 17.42, 19.795, 22.075, 24.94, 25.37, 28.805]
point_label = ["Background", r'${K}_{\alpha}^{Fe}$', r'${K}_{\alpha,\beta}^{Cu}$', r'${K}_{\alpha}^{Nb}$', r'${K}_{\beta}^{Nb}$', r'${K}_{\alpha}^{Mo}$', r'${K}_{\beta}^{Mo}$',
               r'${K}_{\alpha}^{Cd}$', r'${K}_{\beta}^{Cd}$', r'${K}_{\alpha}^{Sn}$', r'${K}_{\beta}^{Sn}$']
counter = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 3, 4, 5, 6, 7, 8, 9
x_sel = np.array([x[k] for k in counter])
peaks_sel = [peaks[k] for k in counter]
peaks_error_sel = [peaks_error[k] for k in counter]
sigmas_sel = np.array([sigmas[k] for k in counter])
sigmas_error_sel = np.array([sigmas_error[k] for k in counter])
point_label_sel = [point_label[k] for k in counter]
with plotting.Plotting(analyzed_data_file=Directory + 'h5_files/tdc_Calibrated_data_' + titles[0] + '.h5') as p:
    a, a_error, b, b_error = p.plot_vcal_energy_calibration(x=x_sel, y=peaks_sel, y_err=peaks_error_sel, point_label=point_label_sel, Directory=Directory, PdfPages=PdfPages, scipy_fit=True, ax2=False)
    cal.plot_calibration_line_kafe(x=x_sel, y=peaks_sel, y_err=peaks_error_sel, xlabel='$\gamma$-peak position from literature [keV]', ylabel=r'$\Delta$VCAL', Directory=Directory, PdfPages=PdfPages, suffix='vcal')
    p.create_Interpolation_perpixel(histogram=hist_tdc_mean, spline_file=spline_file, cols=selected_columns, rows=selected_rows,
                                    n_random_pixels=3, scan_parameter_range=scan_parameter_range, PdfPages=PdfPages)
    cal.plot_spline_masking(calibrated_file=Directory + 'h5_files/tdc_Calibrated_data_' + titles[0] + '.h5', PdfPages=PdfPages)
    source = np.arange(1, 9)
    slope = [28.46, 28.54, 28.60, 28.53, 29.18, 28.46, 28.43, 28.56]
    offset = [40.68, 38.87, 37.46, 38.97, 28.07, 40.35, 40.81, 38.57]
    m, m_error, c, c_error = np.mean(slope), np.absolute(np.std(slope)) / np.sqrt(len(slope)), np.mean(offset), np.absolute(np.std(offset)) / np.sqrt(len(offset))
    cal.plot_calibration_distribution(x=source, y=slope, difference=offset, ticks=point_label[3:], Directory=Directory, PdfPages=PdfPages, suffix='charge_calibration_column', xlabel='Removed source', ylabel=r'slope',
                                      line_color="skyblue", bar_color="blue")
    peak_correction = [(peaks_sel[k] - c) / np.float(m) for k in range(len(peaks_sel))]
    w = 3.65
    charge_correction = [peak_correction[l] * 1000 / np.float(w) for l in range(len(peak_correction))]

    err_peak_correction = [(peaks_error_sel[k]) / np.float(m) for k in range(len(peaks_error_sel))]
    err_charge_correction = [err_peak_correction[n] * 1000 / np.float(w) for n in range(len(err_peak_correction))]
    voltage = [0.2 * peaks_sel[o] * 0.001 for o in range(len(peaks_sel))]  # From DeltaVcal to mV
    x_err = [0.2 * peaks_sel[o] * 0.001 * 0.01 for o in range(len(peaks_sel))]  # error on measurement
    #p.plot_vcal_charge_calibration(x=peaks_sel, y=charge_correction, x_err=peaks_error_sel, point_label=point_label_sel, Directory=Directory, PdfPages=PdfPages)
    #cal.plot_calibration_lines(x=x_sel, y=peaks_sel, y_err=peaks_error_sel, m=m, m_error=m_error, c=c, c_error=c_error, point_label=point_label_sel, Directory=Directory, PdfPages=PdfPages)
    cal.plot_calibration_line_kafe(x=peaks_sel, y=charge_correction, x_err=peaks_error_sel, y_err=err_charge_correction, xlabel=r'$\Delta$VCAL', ylabel=r'Charge[e]', Directory=Directory, PdfPages=PdfPages, suffix='charge')
    cal.plot_calibration_line_kafe(x=voltage, y=charge_correction, y_err=err_charge_correction, x_err=x_err, xlabel=r'Voltage [V]', ylabel=r'Charge[e]', Directory=Directory, PdfPages=PdfPages, suffix='Capacitance')

# Analyze a special source scan
# m = 4
# calibration_file = Directory + 'h5_files/tdc_Calibrated_data_' + titles[m] + '.h5'
# tests_title = ["tdc spectrum for " + titles[m] + " source"]
# with tb.open_file(calibration_file, 'r') as in_file:
#     cluster = in_file.root.Cluster[:]
#     cluster = cluster[cluster["range_status"] == 1]
#     tdc_data = cluster["tdc_value"]
# #cal.source_test(PdfPages=PdfPages, Directory=Directory, tdc_data=tdc_data, tests_title="Cluster", ylabel=r"$\Delta$VCAL", scan_parameter_range=scan_parameter_range)
# cal.plot_tdc_gamma_spectrum_kafe(cluster_hist=cluster, p0=calibrated_fit_parameters[m], scan_parameter_range=scan_parameter_range, cols=selected_columns, title=titles[m], rows=selected_rows,
#                                  cluster_background=cluster_background, background=True, PdfPages=PdfPages, Directory=Directory)
# with plotting.Plotting(analyzed_data_file=source_files[m]) as p:
#     p.plot_tot_tdc_hist(title='Tot vs Tdc histogram for %s source' % titles[m], PdfPages=PdfPages)
PdfPages.close()
