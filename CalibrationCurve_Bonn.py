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
from matplotlib import gridspec
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

    def Inverse_square(self, x, a, b):
        return a / (x + b)**2

    def calibration_curve(self, Directory=False, PdfPages=False, stdev=0.06):
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
        depth = ["3cm", "5cm", "8cm"]
        Voltages = ["30KV", "40KV"]
        colors = ['red', '#006381', '#33D1FF', 'green', 'orange', 'maroon']
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
                        y2 = np.append(y2, (float(row[3]) - float(row[4])) * float(row[5]))
                        bkg_y2 = np.append(bkg_y2, float(row[4]))
                        Factor = np.append(Factor, float(row[5]))
                        difference = np.append(difference, (float(row[3]) - float(row[1])) / float(row[3]) * 100)
                    logging.info("Start Plotting %s cm" % (depth[i]))
                    # Calibrating data with Filter
                    sig1 = [stdev * y1[k] for k in range(len(y1))]
                    popt1, pcov = curve_fit(self.linear, x1, y1, sigma=sig1, absolute_sigma=True, maxfev=5000, p0=(1, 1))
                    chisq1 = self.red_chisquare(np.array(y1), self.linear(x1, *popt1), np.array(sig1), popt1)
                    ax.errorbar(x1, y1, yerr=sig1, color=colors[Voltages.index(volt)], fmt='o')
                    ax.plot(x1, self.linear(x1, *popt1), linestyle=styles[0],
                            color=colors[Voltages.index(volt)], label=volt + " " + "with_Al_Filter")
                    # Calibrating data without Filter
                    sig2 = [stdev * y2[k] for k in range(len(y2))]
                    popt2, pcov = curve_fit(self.linear, x1, y2, sigma=sig2, absolute_sigma=True, maxfev=5000, p0=(1, 1))
                    chisq2 = self.red_chisquare(np.array(y2), self.linear(x1, *popt2), np.array(sig2), popt2)
                    ax.errorbar(x1, y2, yerr=sig2, color=colors[Voltages.index(volt)], fmt='o')
                    ax.plot(x1, self.linear(x1, *popt2), linestyle=styles[1],
                            color=colors[Voltages.index(volt)], label=volt + " " + "without_Al_Filter")
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
            ax.legend()
            ax2.set_xlabel('Tube current (mA)')
            plt.savefig(Directory + "/" + depth[i] + '/CalibrationCurve_Bonn_' + depth[i] + ".png", bbox_inches='tight')
            PdfPages.savefig()

    def Dose_Voltage(self, Directory=False, PdfPages=False, Depth="8cm", test="without_Al_Filter"):
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
            Factor = [10.06]
            facecolors = ['#33D1FF', '#006381', 'green', 'orange', 'maroon', 'red']
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
            plt.plot(xfine, self.quadratic(xfine, *popt), facecolors[i])
            chisq = self.red_chisquare(np.array(y1[i]), self.quadratic(x1[i], *popt), np.array(sig), popt)
            plt.errorbar(x1[i], y1[i], yerr=sig, color=facecolors[i], fmt='o',
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

        # Another fitting using Kafe fit
        for Data in Dataset:
            kafe_Fit = np.append(kafe_Fit, Fit(Data, quadratic_3par))
        for fit in kafe_Fit:
            fit.do_fit()
        kafe_plot = Plot(kafe_Fit[2], kafe_Fit[3])
        kafe_plot.plot_all(show_data_for='all', show_band_for=0)
        kafe_plot.save(Directory + test + "/Dose_Voltage/" + Depth + "/Dose_Voltage_" + Depth + "_kafe_Fit" + ".png")

        PdfPages.savefig()

    def opening_angle(self, Directory=False, Unknown_diameter=np.linspace(3, 10, 20), PdfPages=False, tests=["without_Al_Filter"]):
        '''
        To get the estimated beam diameter relative to the depth
        '''
        for j in range(len(tests)):
            Factor = 9.76  # Calibration Factor
            r = []
            h = []
            with open(Directory + tests[j] +"/Dose_Depth/Dose_Depth_"+tests[j] +".csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    if (float(row[2]) < 100):  # missing data needed to be taken  in the future
                        h = np.append(h, float(row[0]))  # Distance from the source
                        r = np.append(r, float(row[2]))  # Diameter of the beam
            fig2 = plt.figure()
            fig2.add_subplot(111)
            ax2 = plt.gca()
            sig = [0.04 * r[k] for k in range(len(r))]
            ax2.errorbar(h, r, xerr=0.0, yerr=sig, fmt='o', color='black', markersize=3)  # plot points
            popt, pcov = curve_fit(self.linear, h, r, sigma=sig, absolute_sigma=True, maxfev=5000, p0=(1, 1))
            chisq2 = self.red_chisquare(np.array(r), self.linear(h, *popt), np.array(sig), popt)
            line_fit_legend_entry = 'line fit: ax + b\n a=$%.2f\pm%.2f$\nb=$%.2f\pm%.2f$' % (popt[0], np.absolute(pcov[0][0]) ** 0.5, popt[1], np.absolute(pcov[1][1]) ** 0.5)
            ax2.plot(h, self.linear(h, *popt),'-', lw=2, label=line_fit_legend_entry)
            ax2.grid(True)
            ax2.legend(loc="upper right")
            ax2.set_ylabel('Radius (r) [cm]')
            ax2.set_xlabel('Height from the the filter holder(h) [cm]')
            fig2.savefig(Directory + tests[j] + '/opening_angle/Depth_radius_linear' + tests[j] + '.png', bbox_inches='tight')
            PdfPages.savefig()
            h_space= np.linspace(0,h[-1],50)
            r_space = self.linear(h_space,*popt)
            theta = np.degrees(popt[0])
            fig = plt.figure()
            fig.add_subplot(111)
            ax = plt.gca()
            for i in range(len(r_space)):
                x, y = np.linspace(-r_space[i], r_space[i], 2) , [h_space[i] for _ in xrange(2)]
                plt.plot(x, y, linestyle="solid")
            ax.text(0.95, 0.90, "$\Theta^{rad}$ = %.2f\n $h_0$=%.2f$\pm$ %.2f" % (popt[0],popt[1]/popt[0],np.absolute(pcov[1][1]) ** 0.5/popt[0]),
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            #ax.set_title('Diameter covered by beam spot %s'%(tests[j]), fontsize=12)
            ax.invert_yaxis()
            ax.set_xlabel('Diameter (d) [cm]')
            ax.set_ylabel('Height from the the exit window(h) [cm]')
            ax.grid(True)
            fig.savefig(Directory + tests[j] + '/opening_angle/Depth_Diameter_' + tests[j] + '.png', bbox_inches='tight')
            PdfPages.savefig()
            
    def opening_angle2(self, Directory=False, Unknown_diameter=np.linspace(3, 10, 20), PdfPages=False, tests=["without_Al_Filter"]):
        '''
        To get the estimated beam diameter relative to the depth
        '''
        def New_height(dx=15, diameter=False, height=False):
            # the function will give the corresponding height to a specific diameter
            Theta = []
            for i in range(len(diameter)):
                for j in range(len(diameter)):
                    if (i > j):
                        d_diff = diameter[i] - diameter[j]
                        h_diff = height[i] - height[j]
                        Theta = np.append(Theta, d_diff / h_diff)
            hx = (dx - diameter[2]) / np.mean(Theta) + height[2]
            # print "Height for diameter %i cm is %i cm " % (dx, hx)
            return np.round(hx), Theta

        for j in range(len(tests)):
            fig = plt.figure()
            fig.add_subplot(111)
            ax = plt.gca()
            Factor = 9.76  # Calibration Factor
            diameter = []
            height = []
            with open(Directory + tests[j] +"/Dose_Depth/Dose_Depth_"+tests[j] +".csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    if (float(row[2]) < 100):  # missing data needed to be taken  in the future
                        height = np.append(height, float(row[0]))  # Distance from the source
                        diameter = np.append(diameter, float(row[2]) * 2)  # Diameter of the beam
            # calculate the focal point (distance between focal point and window)
            hpf = []
            for l in range(len(diameter[0:4])):
                _, Theta = New_height(dx=diameter[l], diameter=diameter, height=height)
                hpf = np.append(hpf, np.float(diameter[l] / 2.0) / np.float(np.tan(np.mean(Theta / 2))) - height[l])  # hpf=r/tan(theta/2)-h
                print hpf[l], diameter[l], height[l]
            # Unknown_diameter is an array of all the diameters that we might need in irradiation
            #(simply substitute any number ther with your prefered value)
            for k in range(len(Unknown_diameter)):
                Unknown_height, Theta = New_height(dx=Unknown_diameter[k], diameter=diameter, height=height)
                diameter = np.append(diameter, Unknown_diameter[k])
                height = np.append(height, Unknown_height)
            # print Unknown_height,height # Theta    ,diameter
            #plot the cone represents the beam angle   
            for i in range(len(diameter)):
                x = np.linspace(-diameter[i] / 2.0, diameter[i] / 2.0, 10)  # make 10 points of radius from -r to r to draw the line
                y = [height[i] for _ in xrange(10)]
                if i <= 6:  # These values are measured experimentaly
                    linestyle = "solid"
                else:
                    linestyle = "dashed"  # These are Theoritical values
                plt.plot(x, y, linestyle=linestyle)
            ax.text(0.95, 0.90, "$\Theta$ = %.2f$\pm$ %.2f\n $h_{fp}$=%.2f$\pm$ %.2f" % (np.mean(Theta), np.std(Theta), np.mean(hpf), np.std(hpf)),
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            #ax.set_title('Diameter covered by beam spot %s'%(tests[j]), fontsize=12)
            ax.invert_yaxis()
            ax.set_xlabel('Diameter (d) [cm]')
            ax.set_ylabel('Height from the the exit window(h) [cm]')
            ax.grid(True)
            fig.savefig(Directory + tests[j] + '/opening_angle/Depth_Diameter_' + tests[j] + '.png', bbox_inches='tight')
            PdfPages.savefig()
            fig2 = plt.figure()
            fig2.add_subplot(111)
            ax2 = plt.gca()
            d =diameter[:6]
            h = height[:6]
            sig = [0.01 * h[k] for k in range(len(d))]
            ax2.errorbar(h, d, xerr=0.0, yerr=sig, fmt='o', color='black', markersize=3)  # plot points
            line_fit, pcov = np.polyfit(h, d, 1, full=False, cov=True)
            fit_fn = np.poly1d(line_fit)
            line_fit_legend_entry = 'line fit: ax + b\n a=$%.2f\pm%.2f$\nb=$%.2f\pm%.2f$' % (line_fit[0], np.absolute(pcov[0][0]) ** 0.5, line_fit[1], np.absolute(pcov[1][1]) ** 0.5)
            ax2.plot(h, fit_fn(h), '-', lw=2, label=line_fit_legend_entry)
            ax2.grid(True)
            ax2.legend(loc="upper right")
            ax2.set_ylabel('Diameter (d) [cm]')
            ax2.set_xlabel('Height from the the exit window(h) [cm]')
            fig.savefig(Directory + tests[j] + '/opening_angle/Depth_Diameter_linear' + tests[j] + '.png', bbox_inches='tight')
            PdfPages.savefig()
            
    def Dose_Depth(self, Directory=False, colors=False, PdfPages=False, Voltage="40 kV", current="50 mA", stdev=0.6, tests=["without_Al_Filter"], theta=0.16):
        '''
        Relation between the depth and  the Dose rate
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(tests)):
            Factor = 9.76  # Calibration Factor
            height = []
            d1 = []
            y1 = []
            r1 = []
            b1 = []
            with open(Directory + tests[i] +"/Dose_Depth/Dose_Depth_"+tests[i] +".csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    height = np.append(height, float(row[0]))  # Distance from the source
                    y1 = np.append(y1, (float(row[1])))  # Dose rate
                    r1 = np.append(r1, float(row[2]))  # radius of the beam
                    d1 = np.append(d1, float(row[2]) * 2)  # Diameter of the beam
                    b1 = np.append(b1, (float(row[3])) )  # Background
            y1 = [y1[k] - b1[k] for k in range(len(y1))]  # Subtrac Background
            sig = [stdev * y1[k] for k in range(len(y1))]
            y1 = [y1[k]* Factor for k in range(len(y1))]  
            popt1, pcov = curve_fit(self.Inverse_square, height, y1, sigma=sig, absolute_sigma=True, maxfev=5000, p0=(300, 10))
            #chisq1 = self.red_chisquare(np.array(y1), self.Inverse_square(np.array(height), *popt1), sig, popt1)
            ax.errorbar(height, y1, yerr=sig, color=colors[i + 1], fmt='o', label=tests[i])
            xfine = np.linspace(0, height[-1], 100)  # define values to plot the function
            ax.plot(xfine, self.Inverse_square(xfine, *popt1), colors[i + 1], label='Fit: a=%.2f, b=%.2f' % (popt1[0], popt1[1]))
            ax.text(0.9, 0.56, r'$R= \frac{a}{(h+b)^2}$',
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
            #print "The dose rate at %.2f cm depth is " %(45) + str(popt1[0]/(45+popt1[1])**2)+" Mrad/hr "+tests[i]
            ax.set_xlabel('Distance from the beam window(h) [cm]')
            ax.set_title('Dose rate vs distance at  (%s and %s)' % (Voltage, current), fontsize=11)
            ax.set_ylabel('Dose rate (R) [$Mrad(sio_2)/hr$]')
            ax.set_xlim([0, max(height) + 8])
            ax.grid(True)
            ax.legend(loc="upper right")
            ax.ticklabel_format(useOffset=False)
            fig.savefig(Directory + tests[i] + "/Dose_Depth/Dose_Depth_" + tests[i] + ".png", bbox_inches='tight')
        plt.tight_layout()
        PdfPages.savefig()

    def Dose_Depth_inverse(self, Directory=False, colors=False, PdfPages=False, Voltage="40 kV", current="50 mA", stdev=0.1, tests=["without_Al_Filter"], theta=0.16):
        '''
        Relation between the depth and  the Dose rate
        '''
        for i in range(len(tests)):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            Factor = 9.76  # Calibration Factor
            height = []
            diameter = []
            y1 = []
            r1 = []
            b1 = []
            Unknown_radius = []
            with open(Directory + tests[i] +"/Dose_Depth/Dose_Depth_"+tests[i] +".csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    height = np.append(height, float(row[0]))  # Distance from the source
                    y1 = np.append(y1, (float(row[1])) * Factor)  # Dose rate
                    b1 = np.append(b1, (float(row[3])) * Factor)  # Background
            y1 = [y1[k] - b1[k] for k in range(len(y1))]  # Subtrac Background
            inverse = [1 / (height[k] * height[k]) for k in range(len(height))]  # source-object distance
            ax.errorbar(inverse, y1, xerr=0.0, yerr=0.0, fmt='o', color='black', markersize=3)  # plot points
            line_fit, pcov = np.polyfit(inverse, y1, 1, full=False, cov=True)
            fit_fn = np.poly1d(line_fit)
            line_fit_legend_entry = 'line fit: ax + b\n a=$%.2f\pm%.2f$\nb=$%.2f\pm%.2f$' % (line_fit[0], np.absolute(pcov[0][0]) ** 0.5, line_fit[1], np.absolute(pcov[1][1]) ** 0.5)
            ax.plot(inverse, fit_fn(inverse), '-', lw=2, color=colors[i + 1], label=tests[i])
            ax.set_ylabel('Dose rate (R) [$Mrad(sio_2)/hr$]', fontsize=9)
            ax.set_xlabel('1\(distance from window[cm])^2', fontsize=9)
            ax.set_title('Dose rate vs 1\(distance from window[cm])^2 at  (%s and %s)' % (Voltage, current), fontsize=11)
            ax.grid(True)
            ax.legend(loc="upper right")
            fig.savefig(Directory + tests[i] + "/Dose_Depth/Dose_Depth_inverse_" + tests[i] + ".png", bbox_inches='tight')
            plt.tight_layout()
            PdfPages.savefig()

    def Plot_Beam_profile_2d(self, Scan_file=False, Directory=False, Steps=121, width=1, PdfPages=False):
        '''
        Make a 2d scan at specific depth
        '''
        Background = 0.1
        Factor = 10
        with tb.open_file(Scan_file, 'r') as in_file1:
            Map1 = in_file1.root.Mercury_MotorStage[:]
        fig, ax = plt.subplots()
        plt.axhline(y=13, linewidth=2, color='#d62728', linestyle='dashed')
        plt.axvline(x=100, linewidth=2, color='#d62728', linestyle='dashed')
        im = ax.imshow((Map1 * 10e6 - Background) * Factor, aspect='auto', interpolation='gaussian')
        cb = fig.colorbar(im, ax=ax, fraction=0.0594)
        cb.set_label("Dose rate [$Mrad/hr$]")
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y[mm]')
        ax.set_title('Beam profile at 8 cm without collimator support', fontsize=12)
        plt.savefig(Directory + Directory[58:-1] + '2DMap.png')
        PdfPages.savefig()

    def Plot_Beam_profile_3d(self, Scan_file=False, Directory=False, Steps=121, width=1, PdfPages=False):
        '''
        Make a 3d scan at specific depth (The function is under updates)
        '''
        Background = 0.1
        Factor = 10

        def f(x, y):
            with tb.open_file(Scan_file, 'r') as in_file1:
                Map1 = in_file1.root.Mercury_MotorStage[:]
            return (Map1[x, y] * 10e6 - Background) * Factor
        y = np.linspace(0, Steps - 1, Steps - 1, dtype=int)
        x = np.linspace(0, width - 1, width - 1, dtype=int)
        X, Y = np.meshgrid(x, y)
        Z = f(X, Y)
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        plot = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
        scale_x = 10
        scale_y = 10
        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale_x))
        ax.xaxis.set_major_formatter(ticks_x)
        ticks_y = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale_y))
        ax.yaxis.set_major_formatter(ticks_y)
        plt.axhline(y=13, linewidth=2, color='#d62728', linestyle='dashed')
        plt.axvline(x=100, linewidth=2, color='#d62728', linestyle='dashed')
        cb = fig.colorbar(plot, ax=ax, fraction=0.046)
        cb.set_label("Dose rate [$Mrad/hr$]")
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y[mm]')
        ax.set_title('Beam profile at 8 cm without collimator support', fontsize=12)
        plt.savefig(Directory + Directory[58:-1] + '3DMap.png')
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
    Scan_file = Directory + "Mercury_MotorStage.h5"
    tests = ["without_Al_Filter", "with_Al_Filter"]
    colors = ['#33D1FF', 'maroon', '#006381', 'green', 'orange', 'red']
    scan = Calibration_Curves()
#     scan.Plot_Beam_profile_2d(Scan_file=Scan_file, Steps=200, width=20)
    #scan.Plot_Beam_profile_3d(Scan_file=Scan_file, Steps=200, width=20)
    PdfPages = PdfPages('output_data/CalibrationCurve_Bonn' + '.pdf')
    #scan.calibration_curve(stdev=0.04, PdfPages=PdfPages, Directory=Directory)
    scan.opening_angle(Directory=Directory, PdfPages=PdfPages, tests=["without_Al_Filter"])
    scan.Dose_Depth(tests=tests, Directory=Directory, PdfPages=PdfPages, colors=colors)
    scan.Dose_Depth_inverse(tests=tests, Directory=Directory, PdfPages=PdfPages, colors=colors)
    #scan.power_2d(PdfPages=PdfPages, Directory=Directory, V_limit=50, I_limit=50)
    #scan.Dose_Voltage(PdfPages=PdfPages, Directory=Directory, test="without_Al_Filter")
    scan.close()
