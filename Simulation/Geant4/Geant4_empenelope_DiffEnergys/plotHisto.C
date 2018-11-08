{
  gROOT->Reset();
  gStyle->SetOptStat(kFALSE);

   TCanvas* c2 = new TCanvas("cadd", "Hists with different scales");
   c2->Update();
   //c2->SetLogy(1);
  gPad->SetTopMargin(0.12);
  gPad->SetBottomMargin(0.1);
  gPad->SetLeftMargin(0.1);
  gPad->SetRightMargin(0.05);
  gPad->SetFillColor(0);
  gPad->SetTickx();
  gPad->SetTicky();
  gPad->SetGridx();
  //gPad->SetGridy();
  gPad->SetLogy();

  TFile f13("/home/silab62/HEP/geant4.10.01-Example/Results/Geant4_empenelope_DiffEnergys/gammaSpectrum_10keV.root");
  TFile f23("/home/silab62/HEP/geant4.10.01-Example/Results/Geant4_empenelope_DiffEnergys/gammaSpectrum_20keV.root");
  TFile f33("/home/silab62/HEP/geant4.10.01-Example/Results/Geant4_empenelope_DiffEnergys/gammaSpectrum_30keV.root");
  TFile f43("/home/silab62/HEP/geant4.10.01-Example/Results/Geant4_empenelope_DiffEnergys/gammaSpectrum_40keV.root");
  TFile f53("/home/silab62/HEP/geant4.10.01-Example/Results/Geant4_empenelope_DiffEnergys/gammaSpectrum_50keV.root");
  TFile f63("/home/silab62/HEP/geant4.10.01-Example/Results/Geant4_empenelope_DiffEnergys/gammaSpectrum_60keV.root");

  TH1D* h1 = (TH1D*)f13.Get("h3");
  TH1D* h2 = (TH1D*)f23.Get("h3");
  TH1D* h3 = (TH1D*)f33.Get("h3");
  TH1D* h4 = (TH1D*)f43.Get("h3");
  TH1D* h5 = (TH1D*)f53.Get("h3");
  TH1D* h6 = (TH1D*)f63.Get("h3");

//Adding two histograms
 //h1->Add(h2);
 h1->SetMaximum(1000000);
  h1->GetXaxis()->SetLimits(0.,60.);
  h1->Draw("hist E same");
  h1->SetLineColor(1);
  h1->SetLineStyle(9);
  h1->SetLineWidth(2);
  h1->SetMarkerSize(1);
  h1->SetFillColor(1);

  h1->SetTitle("Tungsten Anode Spectrum at different electron Energies");
  h1->GetYaxis()->SetTitle("Counts");
  h1->GetXaxis()->SetTitle("Energy [KeV]");
  cout<<"Entries h1 = "<<h1->GetEntries()<<endl;

  h2->Draw("hist E same");
  h2->SetLineColor(2);
  h2->SetLineStyle(1);
  h2->SetLineWidth(2);
  h2->SetMarkerSize(1);
  h2->SetFillColor(2);
  cout<<"Entries h2 = "<<h2->GetEntries()<<endl;

  h3->Draw("hist E same");
  h3->SetLineColor(4);
  h3->SetLineStyle(1);
  h3->SetLineWidth(2);
  h3->SetMarkerSize(1);
  h3->SetFillColor(4);
  cout<<"Entries h3 = "<<h3->GetEntries()<<endl;

  h4->Draw("hist E same");
  h4->SetLineColor(3);
  h4->SetLineStyle(1);
  h4->SetLineWidth(2);
  h4->SetMarkerSize(1);
  h4->SetFillColor(3);
cout<<"Entries h4 = "<<h4->GetEntries()<<endl;
  h5->Draw("hist E same");
  h5->SetLineColor(6);
  h5->SetLineStyle(1);
  h5->SetLineWidth(2);
  h5->SetMarkerSize(1);
  h5->SetFillColor(6);
cout<<"Entries h5 = "<<h5->GetEntries()<<endl;

  h6->Draw("hist E same");
  h6->SetLineColor(48);
  h6->SetLineStyle(1);
  h6->SetLineWidth(2);
  h6->SetMarkerSize(1);
  h6->SetFillColor(7);
cout<<"Entries h6 = "<<h6->GetEntries()<<endl;

//TLegend *leg = new TLegend(x1, y1,x2,y2);
  TLegend *leg = new TLegend(0.6, 0.65, 0.94,0.80);
//TLegend *leg=new TLegend(0.2,0.2,0.4,0.4);

    leg->AddEntry(h1,"10 Kev","l");
    leg->AddEntry(h2,"20 Kev","l");
    leg->AddEntry(h3,"30 Kev","l");
    leg->AddEntry(h4,"40 Kev","l");
    leg->AddEntry(h5,"50 Kev","l");
    leg->AddEntry(h6,"60 Kev","l");

    leg->SetBorderSize(0.0);
    leg->SetMargin(0.3);
    leg->SetFillColor(0);
    leg->SetFillStyle(10);
    leg->SetLineColor(0);
    leg->SetTextSize(0.025); 
    leg->Draw();
  TPaveText* tText1 = new TPaveText(0.70, 0.90, 0.90, 0.95, "brNDC");
  tText1->SetBorderSize(0);
  tText1->SetFillColor(0);
  tText1->SetFillStyle(0);
  TText *t1 = tText1->AddText("Geant4 Simulation");
  tText1->Draw();
   c2->SaveAs("/home/silab62/HEP/geant4.10.01-Example/Results/Geant4_empenelope_DiffEnergys/secondaryphotons_Creation_log_Diff_Energy.png");





}  

