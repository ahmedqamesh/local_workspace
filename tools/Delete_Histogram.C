#include <iostream>
#include <ostream>
#include <math.h>
using namespace std;
void Delete_Histogram(){
TFile* file = new TFile("gammaSpectrum_Tungsten-Spectrum.root", "update");
file->cd("Histograms/");
gDirectory->Delete("5;1");
file->Close();
}
