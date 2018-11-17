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
			ax.legend()
			plt.tight_layout()
			plt.savefig(Directory+target+"/mass_attenuation_coeff_"+target+".png", bbox_inches='tight')
			PdfPages.savefig()
		        
	def attenuation_thickness(self, Directory=False, PdfPages=False, targets=False, logx= True, logy= True):
		color=['green','black','orange','grey','#006381','#7e0044','black','red']
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
 
 	def attenuation_Energy(self, Directory=False, PdfPages=False,targets=False, logx= True, logy= True, n=False, x_offset=False,y_offset =False):
		color=['green','black','orange','grey','#006381','#7e0044','black','red','#33D1FF',"maroon","yellow", "magenta"]
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
		ax.set_xlabel('Photon energy / keV')
		ax.grid(True)
		ax.set_ylabel('Mass attenuation coefficient / cm$^2$/g')
		ax.set_title(r"Mass attenuation coefficients as a function of Energy", fontsize=10)
		plt.ylim(1,10000)
		plt.xlim(1, 60)
		ax.legend()
		plt.tight_layout()
		plt.savefig(Directory+"/attenuation_Energy_relation.png", bbox_inches='tight')
		PdfPages.savefig()
	
	def attenuation_thickness_RD53(self, Directory=False, PdfPages=False):
	 	fig =plt.figure()
		gs = gridspec.GridSpec(2, 1, height_ratios=[2, 2])
		ax = plt.subplot(gs[0])
		ax1 = plt.subplot(gs[0])
		ax2 = plt.subplot(gs[1])
		def autolabel(rects,total):
			"""
			Attach a text label above each bar displaying its height
			"""
			for rect in rects:
				height = rect.get_height()
				ax2.text(rect.get_x() + rect.get_width()/2., 1.05*height,'%.2f %%' % (height/total*100), ha='center', va='top',fontsize=10,rotation=90)
		Si_rho = 2.32 #g/cm3
		Cu_rho = 8.96 #g/cm3
		Al_rho = 2.70 #g/cm3
		# Energy deposition from Geant4
		Energy_deposition = [16.612,88.628,26.367,2.3403 *1000 ,29.739,485.94,28.618,108.82,10.228, 106.49,9.9527,106.05,9.2885,103.3,9.9909,100.72,9.824,98.55,
							 8.4857,72.163,7.7287]# ev
		total_deposition =np.sum(Energy_deposition)
		Energy_range = ['30 Kev','40 Kev','50 Kev','60 Kev']
		Attenuation_Al = [1.128E+00, 5.684E-01,3.681E-01,2.778E-01]
		Attenuation_Sio2 = [0.859,0.463,0.318,0.252]
		Attenuation_cu = [1.119E-01,9.413E-02,8.363E-02,7.625E-02]
		Al_thickness = [2800] # nano 2.8
		Cu_thickness = [3400,900,220*6,180] #nano 5.8
		Si_thickness = [1000,800,670*2,175*6,310] #nano 4.5
		thickness_Micro =[x*1E-03 for x in [1000,2800,800,3400,670,900,670,220,175,220,175,220,175,220,175,220,175,220,175,180,310]] #Micro
		thickness = [x*1E-07 for x in [1000,2800,800,3400,670,900,670,220,175,220,175,220,175,220,175,220,175,220,175,180,310]] #cm
		total_Thickness =np.sum(thickness_Micro)
		total_metal = ["si02","Al","si02", "cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02","cu","si02"]
		colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon','black']
		for E in np.arange(len(Energy_range)): 
			y=[]
			new_x = []
			att= []
			layer_percent = []
			a =0 
			f = 1
			y_pos = np.arange(len(total_metal))
			# Get the depth as a distance from the first layer
			for i in y_pos:
				new_x = np.append(new_x,round(a, 2))
				a = a+thickness_Micro[i]
				layer_percent = np.append(layer_percent, (thickness_Micro[i]/total_Thickness)*100)
			  
			y = np.append(y,f)	
			for i in np.arange(len(thickness_Micro)):	
				if total_metal[i] == "Al":
					att = np.append(att,float(np.exp(- Attenuation_Al[E] * Si_rho* thickness[i])))
					if E == 0 : 
						Al = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[1])
						rect1 = ax2.bar(i, Energy_deposition[i],color=colors[1], align='center', alpha=0.5)
						autolabel(rect1,total_deposition)
				if total_metal[i] == "cu":
					att = np.append(att,float(np.exp(- Attenuation_cu[E] * Cu_rho* thickness[i])))
					if E == 0 : 
						rect2 = ax2.bar(i, Energy_deposition[i],color=colors[2], align='center', alpha=0.5)
						cu = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[2])
						autolabel(rect2,total_deposition)
				if total_metal[i] == "si02": 
					if i <20:
						att = np.append(att,float(np.exp(- Attenuation_Sio2[E] * Si_rho* thickness[i])))
					else:
						new_x = np.append(new_x,new_x[i]+thickness_Micro[-1])
						att = np.append(att,float(np.exp(- Attenuation_Sio2[E] * Si_rho* thickness[i])))
		
					if E == 0 : 
						sio2 = ax.axvspan(new_x[i],new_x[i+1], alpha=0.5, color=colors[0])
						rect3 = ax2.bar(i, Energy_deposition[i],color=colors[0], align='center', alpha=0.5)
						autolabel(rect3,total_deposition)  
				f = f*att[i]
				y = np.append(y,f)
				
			Energy = ax1.plot(new_x, y, ':',color=colors[E+3], linestyle='dashed', label =Energy_range[E])
			ax1.legend()
		#ax.set_xticks(new_x)
		#ax.set_xticklabels(new_x, rotation=45)
		ax.grid(True,axis='y')
		ax.set_xlabel('Layer Thickness ($\mu m $)')
		ax.set_ylabel('Transmission $I$/$I_0$ ')
		ax.set_title(r'Transmission of x rays through RD53 Metal Layers', fontsize=11)		 
		#ax.legend(handles =[cu,Al,sio2] , labels =["cu", "Al","sio2"])
		ax2.set_yscale('log')
		ax2.set_ylabel('Energy deposited [ev]')
		ax2.set_xlabel("Layer")
		ax2.set_ylim(0.001, 20000)
		ax2.legend(prop={'size': 6})
		ax2.legend(handles =[rect1,rect2,rect3] , labels =["Al","cu", "sio2"])
		ax2.set_title(r'Energy loss of 50 keV x rays through RD53 Metal Layers', fontsize=11)		 
		ax2.grid(True)
		ax2.set_xticks(y_pos)
		ax2.set_xticklabels(total_metal, rotation=45 )
		plt.tight_layout()
		plt.savefig(Directory+'RD53/Thickness_RD53.png', bbox_inches='tight')
		PdfPages.savefig()       		
	def close(self):
		PdfPages.close()

if __name__ == '__main__':
    global PdfPages
    Directory = "Attenuation/"
    targets = ["Al","Fe","pb","Be","W","Ni","Zr","Mn","V","Cu"]
    x_offset = [1.55,10.21,7.3,2.3,6.53,8.5,5.46,17.99,8.97]
    y_offset = [4500,300,430,3500,550,330,700,100,275]
    n=[r'$\mathregular{K}^{\mathregular{Al}}$(1.55  KeV)',
	   r'$\mathregular{L}^{\mathregular{W}}_{I,II,III}$(10.21,11.54,12.1 KeV)',
	   r'$\mathregular{K}^{\mathregular{Fe}}$(7.11 KeV)',
		   r'$\mathregular{L}^{\mathregular{Zr}}_{I,II,III}$(2.22 ,2.30, 2.53 KeV)',
		    r'$\mathregular{K}^{\mathregular{Mn}}$(6.53  KeV)',
		    r'$\mathregular{K}^{\mathregular{Ni}}$(8.33 KeV)',
		     r'$\mathregular{K}^{\mathregular{V}}$(5.46 KeV)',
		      r'$\mathregular{K}^{\mathregular{Zr}}$(17.9 KeV)',
		      r'$\mathregular{K}^{\mathregular{Cu}}$(8.97 KeV)']
		
    PdfPages = PdfPages('output_data/Attenuation' + '.pdf')
    scan = attenuation()
    scan.attenuation_Energy(PdfPages=PdfPages, Directory=Directory, targets =["Al","W","Be","Fe"],x_offset=x_offset,y_offset=y_offset,n = n[0:3])
    scan.attenuation_thickness(PdfPages=PdfPages, Directory=Directory, targets =targets[0:4], logx = True, logy= True)
    #scan.mass_attenuation_coeff(PdfPages=PdfPages, Directory=Directory, targets =targets[1:])
    scan.attenuation_thickness_RD53(PdfPages=PdfPages, Directory=Directory)
    scan.close()
