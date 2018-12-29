#include <iostream>
#include <ostream>
#include <math.h>
using namespace std;
void Root_to_Ascii(){	//Run this using root -l Root_to_Ascii.C > gammaSpectrum_Al-0.15mm-Spectrum.dat &
  gROOT->Reset(); 
  TFile f("/home/silab62/git/XrayMachine_Bonn/xray_build/gammaSpectrum_Al-0.15mm-Spectrum.root");
  TH1D* hist1 = (TH1D*)f.Get("32");
   Int_t n = hist1->GetNbinsX();
   for (Int_t i=1; i<=n; i++) {
   float y = hist1->GetBinContent(i);
   float x = hist1->GetBinLowEdge(i)+hist1->GetBinWidth(i)/2;
   //float logx = log10(x);
      printf("%g %g\n",x,y);
   }

}


