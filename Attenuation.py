from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import csv


class attenuation():
	def mass_attenuation_coeff(self, Directory=False, PdfPages=False, targets=False):
		for target in targets:
			fig = plt.figure()
			ax = fig.add_subplot(111)
			data = loadtxt(Directory + target+"/mass_attenuation_coeff_in_detail_"+target+".dat")
			x = data[:, 0]  # Energy in Kev
			y = data[:, 6]  # total mass attenuation coeff with coherent scattering
			p = data[:, 3]  # mass attenuation coeff due to photoelectric effect
			i = data[:, 2]  # mass attenuation coeff due to compton (incoherent) scattering
			r = data[:, 1]  # mass attenuation coeff due to rayleigh (coherent) scattering
			ppn = data[:, 4]  # mass attenuation coeff due to pair production in nuclei field
			ppe = data[:, 5]  # mass attenuation coeff due to pair production in electron field
			plt.plot(x*10**3, ppe, ':', color='orange', label='Pair production (electron)')
			plt.plot(x*10**3, ppn, ':', color='grey', label='Pair production (nuclei)')
			plt.plot(x*10**3, r, '--', color='green', label='Coherent scattering')
			plt.plot(x*10**3, i, '--', color='#006381', label='Compton scattering')
			plt.plot(x*10**3, p, '-.', color ='#7e0044', label='Photoelectric effect')
			plt.plot(x*10**3, y, '-', color='black', label='Total')
			ax.set_xscale('log')
			ax.set_yscale('log')
			ax.set_xlabel('Photon energy / keV')
			ax.grid(True)
			ax.set_ylabel('Mass attenuation coefficient / cm$^2$/g')
			ax.set_title(r'Mass attenuation coefficient for%s '%target, fontsize=11)
			ax.legend()
			plt.tight_layout()
			plt.savefig(Directory+target+"/mass_attenuation_coeff_"+target+".png", bbox_inches='tight')
			PdfPages.savefig()
		        
	def attenuation_thickness(self, Directory=False, PdfPages=False, targets=False, logx= True, logy= True):
		for target in targets:
			Density =[]
			Mu=[]
			Energy =[]
			x=np.arange(0, 20, 0.001)
			y = []
			fig = plt.figure()
			ax = fig.add_subplot(111)
			with open(Directory + target+"/Attenuation_Energy_"+target+".csv", 'r')as parameters:
				reader = csv.reader(parameters)
				reader.next()
				for row in reader:
					Density = np.append(Density, float(row[0]))
					Mu = np.append(Mu, float(row[1]))
					Energy = np.append(Energy, float(row[2]))
				for i in np.arange(len(Energy)):
					y = np.exp((-1)* Mu[i] * Density[0] * x)
					ax.plot(x, y, ':', label=str(Energy[i])+'Kev')
					if Energy[i] == 60.0:
						l = np.log(10**(-9))/((-1)*Mu[i] * Density[0])
						print "to get 10e-9 of the initial intensity in %s  %5.3f cm shielding is needed"%(target,l) # in Al 31.4 cm , in Iron 2.18 cm, 
	        	ax.annotate("%5.3f cm"%l, xy=(l, 10**(-9)), xytext=(l+1, 10**(-8)),
						arrowprops=dict(arrowstyle="-|>",
						connectionstyle="arc3,rad=-0.5",relpos=(1., 0.),fc="w"))
	        	if target == "Be":
	        		plt.axvline(x=0.03, linewidth=2, color='#d62728', linestyle='solid') # Define the Thickness of our Be window
	        		ax.set_xscale('log')
	        	else :
	        		plt.axvline(x=l, linewidth=2, color='#d62728', linestyle='solid') # Define the shielding thickness
	        		plt.axhline(y=10**(-9), linewidth=2, color='#d62728', linestyle='solid')# Define the shielding thickness
	        	 	plt.ylim(bottom=10**(-10))
	        	 	plt.xlim(0.001, 40)
	        	 	if logx:
	        			ax.set_xscale('log')
	        		if logy:
	        			ax.set_yscale('log')
	        	ax.grid(True)
	        	ax = plt.gca()
	        	
	        	ax.set_xlabel(target+' Thickness (cm)')
	        	ax.set_ylabel('Transmission $I$/$I_0$ ')
	        	ax.legend()
	        	ax.set_title(r'Transmission of x rays through %s Filter'%target, fontsize=11)
	        	
	        	plt.tight_layout()
	        	plt.savefig(Directory+target+"/Thickness_"+target+".png", bbox_inches='tight')
		        PdfPages.savefig()
         		
	def close(self):
		PdfPages.close()

if __name__ == '__main__':
    global PdfPages
    Directory = "Attenuation/"
    targets = ["Al","Be","Fe","pb"]
    PdfPages = PdfPages('output_data/Attenuation' + '.pdf')
    scan = attenuation()
    scan.attenuation_thickness(PdfPages=PdfPages, Directory=Directory, targets =targets[1:], logx = True, logy= True)
    scan.mass_attenuation_coeff(PdfPages=PdfPages, Directory=Directory, targets =targets[1:])
    scan.close()
