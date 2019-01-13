from __future__ import division
from kafe import *
from kafe.function_library import quadratic_3par
from numpy import loadtxt, arange
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.backends.backend_pdf import PdfPages
import csv
from scipy.optimize import curve_fit
import tables as tb
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as ticker
import itertools
from matplotlib.colors import LogNorm
from matplotlib import pyplot as p
from mpl_toolkits.mplot3d import Axes3D    # @UnusedImport
from math import pi, cos, sin
import logging
from scipy.linalg import norm
import os
import matplotlib as mpl
from matplotlib import gridspec
import seaborn as sns
sns.set(style="white", color_codes=True)
from matplotlib.patches import Circle
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea
from mpl_toolkits.axes_grid1 import make_axes_locatable
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")


class Calibration_Curves():
    def linear(self, x, m, c):
        return m * x + c

    def quadratic(self, x, a, b, c):
        return a * x**2 + b * x + c

    def red_chisquare(self, observed, expected, observed_error, popt):
        return np.sum(((observed - expected) / observed_error)**2 / (len(observed_error) - len(popt) - 1))

    def ln(self, x, a, b, c):
        return a * np.log(x + b) - c

    def exp(self, x, a, b, c):
        return a * np.exp(-b * x) + c

    def Inverse_square(self, x, a, b, c):
        return a / (x + b)**2 - c

    def calibration_curve(self, Directory=False, PdfPages=False, stdev=0.06, depth=[0]):
        ''', 
        To get the calibration curves for each current
        For each Measurement you make you need to replace the numbers 0 in Background, Factor, .....by your measurement
        Background =  array of background estimated for each depth
                Cern Results @(40kv and 50 mA)        Bonn Results @(40kv and 50 mA)
        2 cm     0.439 muA    8.577 Mrad/hr            ------ muA    ----- Mrad/hr
        3 cm     0.694 muA    6.714 Mrad/hr            0.4358 muA    4.194 Mrad/hr
        5 cm     0.936 muA    4.402 Mrad/hr            0.3261 muA    3.281 Mrad/hr
        8 cm     0.257 muA    2.471 Mrad/hr            0.2128 muA    2.077 Mrad/hr
#         '''

        Voltages = ["40KV", "30KV"]
        colors = ['#006381', 'red', '#33D1FF', 'green', 'orange', 'maroon']
        styles = ['-', '--']
        for i in range(len(depth)):
            fig = plt.figure()
            #ax = fig.add_subplot(111)
            gs = gridspec.GridSpec(2, 1, height_ratios=[3.5, 0.5])
            ax = plt.subplot(gs[0])
            ax2 = plt.subplot(gs[1])
            for volt in Voltages:
                x1 = []
                y1 = []
                y2 = []
                bkg_y1 = []
                bkg_y2 = []
                Factor = []
                difference = []
                with open(Directory + "/" + depth[i] + "/" + volt + ".csv", 'r')as data:  # Get Data for the first Voltage
                    reader = csv.reader(data)
                    reader.next()
                    for row in reader:
                        x1 = np.append(x1, float(row[0]))
                        y1 = np.append(y1, (float(row[1]) - float(row[2])) * float(row[5]))
                        bkg_y1 = np.append(bkg_y1, float(row[2]))

                        y2 = np.append(y2, (float(row[3]) - float(row[4])) * float(row[5]))  # Data with Al filter
                        bkg_y2 = np.append(bkg_y2, float(row[4]))
                        Factor = np.append(Factor, float(row[5]))
                        difference = np.append(difference, (float(row[3]) - float(row[1])) / float(row[3]) * 100)
                    logging.info("Start Plotting %s cm" % (depth[i]))
                    # Calibrating data with Filter
                    sig1 = [stdev * y1[k] for k in range(len(y1))]
                    popt1, pcov = curve_fit(self.linear, x1, y1, sigma=sig1, absolute_sigma=True, maxfev=5000, p0=(1, 1))
                    chisq1 = self.red_chisquare(np.array(y1), self.linear(x1, *popt1), np.array(sig1), popt1)
                    ax.errorbar(x1, y1, yerr=sig1, color=colors[Voltages.index(volt)], fmt='o')
                    label1 = "(%s,%s ,Fit:D[$Mrad/hr$]=%.3fI[mA] %.3f)" % (volt, "Al Filter", popt1[0], popt1[1])
                    ax.plot(x1, self.linear(x1, *popt1), linestyle=styles[1],
                            color=colors[Voltages.index(volt)], label=label1)
                    # Calibrating data without Filter
                    sig2 = [stdev * y2[k] for k in range(len(y2))]
                    popt2, pcov = curve_fit(self.linear, x1, y2, sigma=sig2, absolute_sigma=True, maxfev=5000, p0=(1, 1))
                    chisq2 = self.red_chisquare(np.array(y2), self.linear(x1, *popt2), np.array(sig2), popt2)
                    ax.errorbar(x1, y2, yerr=sig2, color=colors[Voltages.index(volt)], fmt='o')
                    label2 = "(%s,%s ,Fit:D[$Mrad/hr$]=%.3fI[mA] %.3f)" % (volt, "No Filter", popt1[0], popt1[1])
                    ax.plot(x1, self.linear(x1, *popt2), linestyle=styles[0],
                            color=colors[Voltages.index(volt)], label=label2)
                    sig3 = [stdev * difference[k] for k in range(len(difference))]
                    ax2.errorbar(x1, difference, yerr=sig3, color=colors[Voltages.index(volt)], fmt='o', markersize='1', capsize=2)
                    ax2.set_ylabel('Drop [%]')
                    ax2.yaxis.set_ticks(np.arange(60, 90, step=10))
                    ax2.grid(True)
            plt.ticklabel_format(useOffset=False)
            plt.xlim(0, 60)
            ax.set_title('Calibration curve for ' + depth[i], fontsize=12)
            ax.set_ylabel('Dose rate [$Mrad(sio_2)/hr$]')
            ax.grid(True)
            # ax2.set_ylim(0,101,10)
            ax.legend(prop={'size': 8})
            ax2.set_xlabel('Tube current [mA]')
            plt.savefig(Directory + "/" + depth[i] + '/CalibrationCurve_Bonn_' + depth[i] + ".png", bbox_inches='tight')
            PdfPages.savefig()

    def dose_voltage(self, Directory=False, PdfPages=False, Depth="8cm", test="without_Al_Filter", kafe_Fit=False):
        '''
        Effect of tube Voltage on the Dose
        '''
        y1 = []
        x1 = []
        Dataset = []
        kafe_Fit = []
        fig = plt.figure()
        ax = fig.add_subplot(111)
        Current = ["10mA", "20mA", "30mA", "40mA"]
        for i in range(len(Current)):
            x = []
            y = []
            Background = [0.00801e-06]
            Factor = [9.76]
            with open(Directory + test + "/Dose_Voltage/" + Depth + "/" + Current[i] + ".csv", 'r')as data1:
                reader = csv.reader(data1)
                reader.next()
                for row in reader:
                    x = np.append(x, float(row[0]))
                    y = np.append(y, (float(row[1]) - Background[0]) * Factor[0])
            x1.append(x)
            y1.append(y)
            stdev = 0.06
            sig = [stdev * y1[i][k] for k in range(len(y1[i]))]
            Dataset = np.append(Dataset, build_dataset(x1[i], y1[i], yabserr=sig, title='I=%s' % Current[i], axis_labels=['Voltage (kV)', '$Dose rate [Mrad(sio_2)/hr]$']))
            popt, pcov = curve_fit(self.quadratic, x1[i], y1[i], sigma=sig, absolute_sigma=True, maxfev=5000, p0=(1, 1, 1))
            xfine = np.linspace(0., 60., 100)
            plt.plot(xfine, self.quadratic(xfine, *popt), colors[i])
            chisq = self.red_chisquare(np.array(y1[i]), self.quadratic(x1[i], *popt), np.array(sig), popt)
            plt.errorbar(x1[i], y1[i], yerr=sig, color=colors[i], fmt='o',
                         label='I=%s, Fit: %.3f$\mathrm{x}^2$ + %.3fx %.2f' % (Current[i], popt[0], popt[1], popt[2]))
        ax.set_title('Effect of tube Voltage at ' + Depth + " " + test, fontsize=12)
        ax.set_ylabel('Dose rate [$Mrad(sio_2)/hr$]')
        ax.set_xlabel('Voltage (kV)')
        ax.grid(True)
        ax.legend()
        plt.ticklabel_format(useOffset=False)
        plt.xlim(5, 60)
        plt.ylim(0.1, 7.5)
        # plt.show()
        plt.savefig(Directory + test + "/Dose_Voltage/" + Depth + "/Dose_Voltage_" + Depth + ".png", bbox_inches='tight')
        PdfPages.savefig()

        if kafe_Fit:
            # Another fitting using Kafe fit
            for Data in Dataset:
                kafe_Fit = np.append(kafe_Fit, Fit(Data, quadratic_3par))
            for fit in kafe_Fit:
                fit.do_fit()
            kafe_plot = Plot(kafe_Fit[2], kafe_Fit[3])
            kafe_plot.plot_all(show_data_for='all', show_band_for=0)
            kafe_plot.save(Directory + test + "/Dose_Voltage/" + Depth + "/Dose_Voltage_" + Depth + "_kafe_Fit.png")
            PdfPages.savefig()

    def opening_angle(self, Directory=False, Unknown_diameter=np.linspace(3, 10, 20), PdfPages=False, tests=["without_Al_Filter"]):
        '''
        To get the estimated beam diameter relative to the depth
        '''
        # Using contourf to provide my colorbar info, then clearing the figure
        Z = [[0, 0], [0, 0]]

        # plt.clf()
        for j in range(len(tests)):
            r = []
            h = []
            std = []
            with open(Directory + tests[j] + "/opening_angle/opening_angle_" + tests[j] + ".csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    h = np.append(h, float(row[0]))  # Distance from the source
                    r = np.append(r, float(row[1]))  # Diameter of the beam
                    std = np.append(std, float(row[2]))  # Diameter of the beam
            fig2 = plt.figure()
            fig2.add_subplot(111)
            ax2 = plt.gca()
            ax2.errorbar(h, r, xerr=0.0, yerr=std, fmt='o', color='black', markersize=0.9, ecolor='black')  # plot points

            popt, pcov = curve_fit(self.linear, h, r, sigma=std, absolute_sigma=True, maxfev=5000, p0=(1, 1))
            chisq2 = self.red_chisquare(np.array(r), self.linear(h, *popt), np.array(std), popt)
            line_fit_legend_entry = 'line fit: ax + b\n a=$%.3f\pm%.3f$\nb=$%.3f\pm%.3f$' % (popt[0], np.absolute(pcov[0][0]) ** 0.5, popt[1], np.absolute(pcov[1][1]) ** 0.5)

            ax2.plot(h, self.linear(h, *popt), '-', lw=1, label=line_fit_legend_entry)
            cmap = plt.cm.get_cmap('viridis', 15)
            h_space = np.linspace(h[0], h[-1], 50)
            # the function uses the fit parameters in dose_depth_scan
            sc = ax2.scatter(h_space, self.linear(h_space, *popt), c=self.Inverse_square(h_space, a=1410.29, b=6.27, c=0.14),
                             cmap=cmap, s=50,)
            cb = fig2.colorbar(sc, ax=ax2, orientation='horizontal')
            cb.ax.invert_xaxis()
            cb.set_label("Dose rate [$Mrad/hr$]")
            ax2.set_title('Radius covered by beam spot %s (40kv and 50 mA)' % (tests[j]), fontsize=12)
            ax2.grid(True)
            ax2.legend()
            ax2.set_ylabel('Radius (r) [cm]')
            ax2.set_xlabel('Height from the  collimator holder(h) [cm]')
            fig2.savefig(Directory + tests[j] + '/opening_angle/Depth_radius_linear' + tests[j] + '.png', bbox_inches='tight')
            PdfPages.savefig()

            r_space = self.linear(h_space, m=popt[0], c=popt[1])
            fig = plt.figure()
            fig.add_subplot(111)
            ax = plt.gca()
            for i in range(len(r_space)):
                x, y = np.linspace(-r_space[i], r_space[i], 2), [h_space[i] for _ in xrange(2)]
                plt.plot(x, y, linestyle="solid")
            ax.text(0.95, 0.90, "$\Theta^{rad}$ = %.3f$\pm$ %.3f\n $h_{0}$=%.3f$\pm$ %.3f" % (2 * popt[0], 2 * np.absolute(pcov[0][0]) ** 0.5, popt[1] / (popt[0]), np.absolute(pcov[1][1]) ** 0.5 / popt[0]),
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            ax.set_title('Diameter covered by beam spot %s' % (tests[j]), fontsize=12)
            ax.invert_yaxis()
            ax.set_xlabel('Diameter (d) [cm]')
            ax.set_ylabel('Height from the the collimator holder(h) [cm]')
            ax.grid(True)
            fig.savefig(Directory + tests[j] + '/opening_angle/Depth_Diameter_' + tests[j] + '.png', bbox_inches='tight')
            PdfPages.savefig()

    def dose_depth(self, Directory=False, colors=False, PdfPages=False, Voltage="40 kV", current="50 mA", stdev=0.2, tests=["without_Al_Filter"], theta=0.16):
        '''
        Relation between the depth and  the Dose rate
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(tests)):
            Factor = 9.81  # Calibration Factor
            height = []
            y1 = []
            b1 = []
            with open(Directory + tests[i] + "/Dose_Depth/Dose_Depth_" + tests[i] + ".csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    height = np.append(height, float(row[0]))  # Distance from the source
                    y1 = np.append(y1, (float(row[1])))  # Dose rate
                    b1 = np.append(b1, (float(row[2])))  # Background
            y1 = [y1[k] - b1[k] for k in range(len(y1))]  # Subtract Background
            sig = [stdev * y1[k] for k in range(len(y1))]
            y1 = [y1[k] * Factor for k in range(len(y1))]
            popt1, pcov = curve_fit(self.Inverse_square, height, y1, sigma=sig, absolute_sigma=True, maxfev=500, p0=(300, 6, 0))
            chisq1 = self.red_chisquare(np.array(y1), self.Inverse_square(np.array(height), *popt1), sig, popt1)
            ax.errorbar(height, y1, yerr=sig, color=colors[i + 1], fmt='o', label=tests[i], markersize='4')
            xfine = np.linspace(height[0], height[-1], 100)  # define values to plot the function
            ax.plot(xfine, self.Inverse_square(xfine, *popt1), colors[i + 1], label='Fit: a=%.2f, b=%.2f, c=%.2f' % (popt1[0], popt1[1], popt1[2]))
            ax.text(0.9, 0.56, r'$R= \frac{a}{(h+b)^2}-c$',
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
            # print "The dose rate at %.2f cm depth is " %(45) + str(popt1[0]/(45+popt1[1])**2)+" Mrad/hr "+tests[i]
            ax.set_xlabel('Distance from the collimator holder(h) [cm]')
            ax.set_title('Dose rate vs distance at  (%s and %s)' % (Voltage, current), fontsize=11)
            ax.set_ylabel('Dose rate (R) [$Mrad(sio_2)/hr$]')
            ax.set_xlim([0, max(height) + 8])
            ax.grid(True)
            ax.legend(loc="upper right")
            ax.ticklabel_format(useOffset=False)
            fig.savefig(Directory + tests[i] + "/Dose_Depth/Dose_Depth_" + tests[i] + ".png", bbox_inches='tight')  # 1.542

        plt.tight_layout()
        PdfPages.savefig()

        # check the fit
        fig = plt.figure()
        ax2 = fig.add_subplot(111)
        inverse = self.Inverse_square(height, *popt1)
        ax.errorbar(inverse, y1, xerr=0.0, yerr=0.0, fmt='o', color='black', markersize=3)  # plot points
        line_fit, pcov = np.polyfit(inverse, y1, 1, full=False, cov=True)
        fit_fn = np.poly1d(line_fit)
        line_fit_legend_entry = 'line fit: ax + b\n a=$%.2f\pm%.2f$\nb=$%.2f\pm%.2f$' % (line_fit[0], np.absolute(pcov[0][0]) ** 0.5, line_fit[1], np.absolute(pcov[1][1]) ** 0.5)
        ax2.plot(inverse, fit_fn(inverse), '-', lw=2, color=colors[i + 1], label=tests[i])
        ax2.set_ylabel('Dose rate (R) [$Mrad(sio_2)/hr$]', fontsize=9)
        ax2.set_xlabel(r'$R= \frac{a}{(h+b)^2}-c$', fontsize=9)
        ax2.set_title('(%s and %s)' % (Voltage, current), fontsize=11)
        ax2.grid(True)
        ax2.legend(loc="upper right")
        fig.savefig(Directory + tests[i] + "/Dose_Depth/Dose_Depth_inverse_" + tests[i] + ".png", bbox_inches='tight')
        plt.tight_layout()
        PdfPages.savefig()

    def calibration_temprature(self, data=None, PdfPages=False, Directory=False, colors=None):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax2 = ax.twinx()
        Factor = 9.62  # Calibration Factor
        plot_lines = []
        with tb.open_file(data) as in_file:
            temprature_dose = in_file.root.temprature_dose[:]
            time = temprature_dose["time"]
            current = temprature_dose["current"] * 10**6
            temprature = temprature_dose["temprature"]
        temp = ax2.errorbar(time, temprature, yerr=0.0, color=colors[0], fmt='-')
        curr = ax.errorbar(time[1:], current[1:], fmt='-', color=colors[1])
        ax2.set_ylabel('Temprature[$^oC$]')
        ax.set_ylabel('current [$\mu$ A]')
        ax.set_xlabel('time [Seconds]')
        ax.grid(True)
        ax.set_ylim([0, 1])
        plot_lines.append([temp, curr])
        plt.legend(plot_lines[0], ["temprature", "mean current=%0.2f $\mu$ A" % np.mean(current)])
        plt.savefig(Directory + 'without_Al_Filter/temprature/temprature_dose.png')
        plt.tight_layout()
        PdfPages.savefig()

    def Plot_Beam_profile_2d(self, Directory=False, PdfPages=False, depth=None):
        '''
        Make a 2d scan at specific depth
        '''
        Factor = 9.76  # Calibration Factor
        Background = 0.005
        binwidth = 1
        for d in range(len(depth)):
            with tb.open_file(Directory + "without_Al_Filter/beamspot/" + depth[d] + "/beamspot_" + depth[d] + ".h5", 'r') as in_file:
                beamspot = in_file.root.beamspot[:]
                beamspot = (beamspot * 1000000 - Background) * Factor
            # The aim of the correction is to overcome the problem happened during measurment
            # because of the timming difference between z and x direction
            corrected_beamspot = np.zeros(shape=(beamspot.shape[0], beamspot.shape[1]), dtype=np.float64)
            for z in np.arange(beamspot.shape[0]):
                for x in np.arange(beamspot.shape[1]):
                    if z % 2 == 0:
                        corrected_beamspot[z, x] = beamspot[z, x]
                    else:
                        if depth[d] == "3cm":
                            radius = r'$r=0.65 \pm 0.05$ cm'
                        if depth[d] == "51cm":
                            radius = r'$r=4 \pm 0.05$ cm'
                        if depth[d] == "8cm":
                            radius = r'$r=1 \pm 0.05$ cm'
            fig, ax = plt.subplots()
            mid_x = beamspot.shape[0]
            mid_z = beamspot.shape[1]
            plt.axhline(y=mid_z / 2, linewidth=1, color='#d62728', linestyle='dashed')
            plt.axvline(x=mid_x / 2, linewidth=1, color='#d62728', linestyle='dashed')

            cmap = plt.cm.get_cmap('viridis', 20)
            im = ax.imshow(beamspot, aspect='auto', interpolation='gaussian', cmap=cmap)
            cb = fig.colorbar(im, ax=ax, fraction=0.0594)
            # create new axes on the right and on the top of the current axes
            divider = make_axes_locatable(ax)
            axHistx = divider.append_axes("top", 1.2, pad=0.2, sharex=ax)
            axHisty = divider.append_axes("right", 1.2, pad=0.2, sharey=ax)
            axHistx.bar(x=range(beamspot.shape[1]), height=np.ma.sum(beamspot, axis=0), align='center',
                        linewidth=0, color=(0.2, 0.4, 0.6, 0.6), edgecolor='black')

            # make some labels invisible
            plt.setp(axHistx.get_xticklabels() + axHisty.get_yticklabels(), visible=False)
            axHistx.set_ylabel('Dose rate [$Mrad/hr$]')
            axHisty.set_ylabel('Dose rate [$Mrad/hr$]')
            axHisty.barh(y=range(beamspot.shape[0]), width=np.ma.sum(beamspot, axis=1), align='center',
                         linewidth=0, color=(0.2, 0.4, 0.6, 0.6), edgecolor='black')

            cb.set_label("Dose rate [$Mrad/hr$]")
            ax.text(0.9, 0.9, radius,
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
            ax.set_xlabel('x [mm]')
            ax.set_ylabel('y[mm]')
            plt.title("Beam profile at " + depth[d] + " from the collimator holder (%s and %s)" % ("40 kV", "50mA"), fontsize=12, y=1.7, x=-0.6)
            plt.savefig(Directory + "without_Al_Filter/beamspot/" + depth[d] + "/beamspot_" + depth[d] + "_2d.png")
            PdfPages.savefig()

    def Plot_Beam_profile_3d(self, Directory=False, PdfPages=False, depth=[0]):
        '''
        Make a 3d scan at specific depth (The function is under updates)
        '''
        def f(x, y, Factor=9.62, Background=0.012, beamspot=None):
            return (beamspot[y, x] * 1000000 - Background) * Factor
        for d in range(len(depth)):
            with tb.open_file(Directory + "without_Al_Filter/beamspot/" + depth[d] + "/beamspot_" + depth[d] + ".h5", 'r') as in_file:
                beamspot = in_file.root.beamspot[:]
            y = np.linspace(0, beamspot.shape[0] - 1, 100, dtype=int)
            x = np.linspace(0, beamspot.shape[1] - 1, 100, dtype=int)
            X, Y = np.meshgrid(x, y)
            Z = f(X, Y, beamspot=beamspot)

            fig = plt.figure()
            ax = fig.gca(projection='3d')
            plot = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
            plt.axhline(y=25, linewidth=2, color='#d62728', linestyle='dashed')
            plt.axvline(x=16, linewidth=2, color='#d62728', linestyle='dashed')
            cb = fig.colorbar(plot, ax=ax, fraction=0.046)
            cb.set_label("Dose rate [$Mrad/hr$]")
            ax.set_xlabel('x [mm]')
            ax.set_ylabel('y[mm]')
            plt.axis('off')
            ax.set_title("Beam profile at " + depth[d] + "without collimator support", fontsize=12)
            plt.savefig(Directory + "without_Al_Filter/beamspot/" + depth[d] + "/beamspot_" + depth[d] + "_3d.png")
            PdfPages.savefig()

    def power_2d(self, Directory=False, PdfPages=False, size_I=50, size_V=60, V_limit=50, I_limit=50):
        '''
        Calculate the power in each point of I and V
        '''

        Power = np.zeros(shape=(size_I, size_V), dtype=float)
        power_max = np.zeros(shape=(size_I, size_V), dtype=float)
        p_max = V_limit * I_limit
        V = np.arange(0, size_V, 1)
        for i in range(size_I):
            for v in range(len(V)):
                Power[i, v] = i * v
                if (i * v == p_max):
                    power_max[i, v] = i * v
        fig, ax = plt.subplots()
        im = ax.imshow(Power, aspect='auto', origin='lower', interpolation='gaussian', cmap=plt.get_cmap('tab20c'))
        cb = fig.colorbar(im, ax=ax, fraction=0.0594)
        cb.set_label("Power [W]")
        ax.set_xlabel('Voltage [kV]')
        ax.set_ylabel('Current [mA]')
        ax.set_xlim([0, len(V)])
        ax.set_ylim([0, size_I])
        ax.set_title('Power of x-ray tube ', fontsize=12)
        ax.grid()
        ax2 = ax.twinx()
        x, y = np.where(power_max)
        ax2.axis('off')
        ax2.set_ylim([0, size_I])
        plt.axhline(y=I_limit, linewidth=2, color='#d62728', linestyle='solid')
        plt.axvline(x=V_limit, linewidth=2, color='#d62728', linestyle='solid')
        plt.tight_layout()
        plt.savefig(Directory + 'Power.png')
        PdfPages.savefig()

    def close(self):
        PdfPages.close()


if __name__ == '__main__':
    global PdfPages
    Directory = "Calibration_Curves/"
    tests = ["without_Al_Filter", "with_Al_Filter"]
    depth = ["3cm", "5cm", "8cm", "51cm"]
    colors = ['red', '#006381', '#7e0044', "maroon", 'grey', 'green', 'orange', "magenta", '#33D1FF', 'black', '#7e0044', 'black', "yellow"]
    scan = Calibration_Curves()
    PdfPages = PdfPages('output_data/CalibrationCurve_Bonn' + '.pdf')
    scan.Plot_Beam_profile_2d(Directory=Directory, PdfPages=PdfPages, depth=["3cm", "8cm", "51cm"])
    scan.Plot_Beam_profile_3d(Directory=Directory, PdfPages=PdfPages, depth=["3cm", "8cm", "51cm"])
    #scan.calibration_curve(stdev=0.04, PdfPages=PdfPages, Directory=Directory,depth=["51cm"])
    scan.opening_angle(Directory=Directory, PdfPages=PdfPages, tests=["without_Al_Filter"])
    #scan.dose_depth(tests=tests, Directory=Directory, PdfPages=PdfPages, colors=colors)
    scan.calibration_temprature(data=Directory + "without_Al_Filter/temprature/temprature_dose.h5",
                                colors=colors, Directory=Directory, PdfPages=PdfPages)
    #scan.power_2d(PdfPages=PdfPages, Directory=Directory, V_limit=50, I_limit=50)
    #scan.dose_voltage(PdfPages=PdfPages, Directory=Directory, test="without_Al_Filter", kafe_Fit=False)
    scan.close()
