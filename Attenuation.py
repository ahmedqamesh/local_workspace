from numpy import loadtxt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import csv
from matplotlib import gridspec

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
			ax.set_title(r'Mass attenuation coefficient for %s '%target, fontsize=11)
			ax.legend(loc="upper right")
			plt.tight_layout()
			plt.savefig(Directory+target+"/mass_attenuation_coeff_"+target+".png", bbox_inches='tight')
			PdfPages.savefig()
		        
	def attenuation_thickness(self, Directory=False, PdfPages=False, targets=False, logx= True, logy= True,color=None):
		
		
		for target in targets:
			Density =[]
			Mu=[]
			Energy =[]
			x=np.arange(0, 20, 0.001)
			y = []
			with open(Directory + target+"/Attenuation_Energy_"+target+".csv", 'r')as parameters:
				fig = plt.figure()
				ax = fig.add_subplot(111)
				reader = csv.reader(parameters)
				reader.next()
				for row in reader:
					Density = np.append(Density, float(row[0]))
					Mu = np.append(Mu, float(row[1]))
					Energy = np.append(Energy, float(row[2]))
				for i in np.arange(len(Energy)):
					y = np.exp((-1)* Mu[i] * Density[0] * x)
					ax.plot(x, y, ':', label=str(Energy[i])+'Kev')
					if ((Energy[i] == 60.0) and (target != "Be")):
						l = np.log(10**(-9))/((-1)*Mu[i] * Density[0])
						print "to get 10e-9 of the initial intensity in %s  %5.3f cm shielding is needed"%(target,l)
						ax.annotate("%5.3f cm"%l, xy=(l, 10**(-9)), xytext=(l+1, 10**(-8)),
								arrowprops=dict(arrowstyle="-|>",connectionstyle="arc3,rad=-0.5",relpos=(.6, 0.),fc="w"))
						ax.axvline(x=l, linewidth=2, color='#d62728', linestyle='solid') # Define the shielding thickness
	        			#ax.axhline(y=10**(-9), linewidth=2, color='#d62728', linestyle='solid')# Define the shielding thickness
	        	 		ax.set_ylim(bottom=10**(-10))
	        	 		ax.set_xlim(0.001, 150)
	        	 		#ax.set_yscale('log')
        		if target == "Be":
					ax.axvline(x=0.03, linewidth=2, color='#d62728', linestyle='solid')
					ax.annotate("%5.3f cm"%0.03, xy=(0.03, 0), xytext=(0.03+0.1, 0.2),
						arrowprops=dict(arrowstyle="-|>",
						connectionstyle="arc3,rad=-0.5",relpos=(.2, 0.),fc="w"))
					ax.set_xlim(0.001, 10)
		 	if logx:
				ax.set_xscale('log')
			ax.grid(True)
			ax.set_xlabel(target+' Thickness (cm)')
			ax.set_ylabel('Transmission $I$/$I_0$ ')
			ax.legend(loc='upper right')
			ax.set_title(r'Transmission of x rays through %s Filter'%target, fontsize=11)
			plt.tight_layout()
			plt.savefig(Directory+target+"/Thickness_"+target+".png", bbox_inches='tight')
			PdfPages.savefig()
 
 	def attenuation_Energy(self, Directory=False, PdfPages=False,targets=False, logx= True, logy= True, n=False, x_offset=False,y_offset =False,color = None):
		
		fig = plt.figure()
		ax = fig.add_subplot(111)
		for i in np.arange(len(targets)):
			data = loadtxt(Directory + targets[i]+"/mass_attenuation_coeff_in_detail_"+targets[i]+".dat")
			x = data[:, 0]  # Energy in Kev
			y = data[:, 6]  # total mass attenuation coeff with coherent scattering
			ax.plot(x*10**3, y, '-', color=color[i], label=targets[i])
		ax = plt.gca()#.invert_xaxis()
		for j, txt in enumerate(n):
			ax.annotate(txt,xy=(x_offset[j],y_offset[j]),color=color[j], size=6)
		ax.set_xscale('log')
		ax.set_yscale('log')
		ax.set_xlabel('Photon energy [keV]')
		ax.grid(True)
		ax.set_ylabel('Mass attenuation coefficient [cm$^2$/g]')
		#ax.set_title(r"Mass attenuation coefficients as a function of Energy", fontsize=10)
		plt.ylim(1,10000)
		plt.xlim(1, 60)
		ax.legend()
		plt.tight_layout()
		plt.savefig(Directory+"/attenuation_Energy_relation.png", bbox_inches='tight')
		PdfPages.savefig()
  		
	def close(self):
		PdfPages.close()

if __name__ == '__main__':
    global PdfPages
    Directory = "Attenuation/"
    targets = ["Al","W","Fe","Mn","Ni","V","Zr"]#,"Be","pb","Cu"]
    x_offset = [1.55,11,7.3,6.53,8.5,5.46,2.3,17.99]#,8.97]
    y_offset = [4500,260,400,550,330,700,3500,100]#,275]
    color=['green',"red",'orange','grey','#006381','#7e0044','black','black','#33D1FF',"maroon","yellow",'magenta']
    n=[r'$\mathregular{K}^{\mathregular{Al}}$(1.55  KeV)',
	   r'$\mathregular{L}^{\mathregular{W}}_{I,II,III}$(10.21,11.54,12.1 KeV)',
	   r'$\mathregular{K}^{\mathregular{Fe}}$(7.11 KeV)',
		    r'$\mathregular{K}^{\mathregular{Mn}}$(6.53  KeV)',
		    r'$\mathregular{K}^{\mathregular{Ni}}$(8.33 KeV)',
		     r'$\mathregular{K}^{\mathregular{V}}$(5.46 KeV)',
		     r'$\mathregular{L}^{\mathregular{Zr}}_{I,II,III}$(2.22 ,2.30, 2.53 KeV)',
		      r'$\mathregular{K}^{\mathregular{Zr}}$(17.9 KeV)']#,r'$\mathregular{K}^{\mathregular{Cu}}$(8.97 KeV)']
		
    PdfPages = PdfPages('output_data/Attenuation' + '.pdf')
    scan = attenuation()
    scan.attenuation_Energy(PdfPages=PdfPages, Directory=Directory, targets =targets,x_offset=x_offset,y_offset=y_offset,n = n[0:],color=color)
    #scan.attenuation_thickness(PdfPages=PdfPages, Directory=Directory, targets =targets[0:4], logx = True, logy= True,color=color)
    #scan.mass_attenuation_coeff(PdfPages=PdfPages, Directory=Directory, targets =targets[:])
    scan.close()
