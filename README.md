# XrayMachine_Bonn
# Links
Geant4 :http://geant4.cern.ch/support/download.shtml
Attenuation Data: http://henke.lbl.gov/optical_constants/
http://physics.nist.gov/PhysRefData/XrayMassCoef/tab3.html (only mass absorption coeff Low range)
http://physics.nist.gov/cgi-bin/Xcom/xcom3_1
http://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html  (mass abs coeff  with photoeffekt, compton usw..)	
https://physics.nist.gov/PhysRefData/XrayTrans/Html/search.html			 (X-ray transition energies by element(s), transition(s), and/or energy/wavelength range. )  
# Need to install 
pip install lmfit

#Geant4 installation
wget http://geant4.cern.ch/support/source/geant4.10.01.p01.tar.gz
cmake -DGEANT4_USE_GDML=ON -DGEANT4_INSTALL_DATA=ON -DGEANT4_USE_G3TOG4=ON -DGEANT4_USE_OPENGL_X11=ON -DCMAKE_INSTALL_PREFIX=/home/silab62/HEP/geant4.10.01-install -DGEANT4_BUILD_MULTITHREADED=ON -DGEANT4_USE_QT=ON -DCLHEP_ROOT_DIR=/home/silab62/HEP/Tools/clhep/install ../geant4.10.01.p01
make -j
make install
source /home/silab62/HEP/geant4-install/bin/geant4.sh


#CLHEP installation  
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

#Root installation 
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
