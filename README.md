# MyWorkSpace includes a set of libraries and functions for analysis and plotting.
#Step-by-step Installation Guide
The following step-by-step installation guide explains in detail how you can setup under Windows, Linux or OS X operating system. This guide addresses users, that do not have python or git experience.
Make an Installation Directory for all the installed packages

Installing Miniconda Python
Miniconda Python is a Python distribution providing a simple to use package manager to install lots of Python packages for data analysis, plotting and I/O. These packages are heavily used in pyBAR.
Download and install Miniconda by following this link: Continuum Miniconda. PyBar supports Python 2.7.x but not Python 3 and newer.
Note: Select the Python 2.7 version according to your operating system architecture (e.g. 64-bit Python on 64-bit operating system)
Note: We strongly recommend installing a 64-bit operating system.
 
Installing C++ Compiler
Linux: Install gcc via package manager, e.g. on Ubuntu run:
sudo apt-get install build-essential
Windows: Install Microsoft Visual C++ Compiler for Python 2.7
OS X: Install Xcode from App Store and install Xcode Command Line Tools by running:
xcode-select --install
Installing Eclipse with PyDev
Eclipse is a state of the art Integrated Development Environment (IDE) for almost every important software programming language (JAVA, C++, Python, Fortran, Ruby, Mathematica). It has a plug in system to extend the development environment. PyDev is the Python IDE plugin for Eclipse.
Eclipse needs a Java runtime environmet (JRE) and will not start if this is not installed. Windows: It is recommend to use the Eclipse 32-bit version, even on a 64-bit machine. Since Eclipse 64-bit needs JRE 64-bit and Oracle JRE 64-bit does not provide automatic updates. This puts the PC at risk of viruses.
Download the Eclipse installer from Eclipse Homepage and choose Eclipse for C/C++ developers during installation.
Eclipse asks for a workspace path where the projects will be located on your hard drive. Standard settings are sufficient.
Close the welcome screen.
Install the PyDev plugin by clicking on Help → Install New Software . Press add and fill the form (name = PyDev, location = http://pydev.org/updates):
<img src = "images/PyDev.jpg">
Select PyDev and install (accept license agreement and trust the certificate).
Add PyDev perspective to Eclipse and select it. The button is located in the upper rigt corner:
<img src = "images/Perspective.jpg">
Goto Window → Preferences → PyDev → Interpreters→ Python Interpreter and press new.
<img src = "images/AnacondaSetup1.jpg">
Select the Python executable in /home//miniconda/bin/ on Linux or c:\Miniconda\ on Windows (optionally use the Miniconda/env// folder if you are using Miniconda environments) and press the OK button. Everything is set up automatically.
More details are given here. https://docs.continuum.io/anaconda/ide_integration/
# Links
Geant4 :http://geant4.cern.ch/support/download.shtml
Attenuation Data: http://henke.lbl.gov/optical_constants/
http://physics.nist.gov/PhysRefData/XrayMassCoef/tab3.html (only mass absorption coeff Low range)
http://physics.nist.gov/cgi-bin/Xcom/xcom3_1
http://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html  (mass abs coeff  with photoeffekt, compton usw..)	
https://physics.nist.gov/PhysRefData/XrayTrans/Html/search.html			 (X-ray transition energies by element(s), transition(s), and/or energy/wavelength range. )  
# Need to install 
pip install lmfit

# Geant4 installation
wget http://geant4.cern.ch/support/source/geant4.10.01.p01.tar.gz
cmake -DGEANT4_USE_GDML=ON -DGEANT4_INSTALL_DATA=ON -DGEANT4_USE_G3TOG4=ON -DGEANT4_USE_OPENGL_X11=ON -DCMAKE_INSTALL_PREFIX=/home/silab62/HEP/geant4.10.01-install -DGEANT4_BUILD_MULTITHREADED=ON -DGEANT4_USE_QT=ON -DCLHEP_ROOT_DIR=/home/silab62/HEP/Tools/clhep/install ../geant4.10.01.p01
make -j
make install
source /home/silab62/HEP/geant4-install/bin/geant4.sh


# CLHEP installation  
mkdir Tools 
mkdir build install source
cd /home/silab62/HEP/Tools/clhep/build/
mkdir clhep-2.1.3.1
cd clhep-2.1.3.1
cmake ../../source/clhep/
ccmake .
#change CMAKE_INSTALL_PREFIX to /home/silab62/HEP/Tools/clhep/install/
make 
make install

# Root installation 
sudo apt-get install git dpkg-dev make g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev
sudo apt-get install build-essential git subversion
sudo apt-get install gfortran libssl-dev libpcre3-dev xlibmesa-glu-dev libglew1.5-dev libftgl-dev libmysqlclient-dev libfftw3-dev cfitsio-dev graphviz-dev libavahi-compat-libdnssd-dev libldap2-dev python-dev libxml2-dev libkrb5-dev libgsl0-dev libqt4-dev ccache
sudo apt-get install xfs xfstt
sudo apt-get install t1-xfree86-nonfree ttf-xfree86-nonfree ttf-xfree86-nonfree-syriac xfonts-75dpi xfonts-100dpi


./configure --all --prefix=/home/silab62/HEP/Tools/root6/install
make -j 4
make install
nano ~/.bashrc
#Add the line
source ~/bin/thisroot.sh
export PATH=$ROOTSYS/bin:$PATH
export LD_LIBRARY_PATH=$ROOTSYS/lib:$LD_LIBRARY_PATH

#For Ubuntu 14.04 run: sudo mkdir /usr/include/freetype && sudo cp /usr/include/freetype2/freetype.h /usr/include/freetype/freetype.h
To unistall 
sudo apt-get remove root-system-bin
sudo apt-get remove --auto-remove root-system-bin
