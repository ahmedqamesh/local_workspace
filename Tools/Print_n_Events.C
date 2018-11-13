{
  gROOT->Reset();
  gStyle->SetOptStat(kFALSE);
  TFile f13("/home/silab62/HEP/geant4.10.01-Example/TestEm3_build_Trash/RD53_NoMetal_Layers.root");//TestEm3_build_Trash //Xray_Test_Build
  TH1D* h1 = (TH1D*)f13.Get("51");
  TH1D* h2 = (TH1D*)f13.Get("52");
  TH1D* h3 = (TH1D*)f13.Get("53");
  TH1D* h4 = (TH1D*)f13.Get("54");
  TH1D* h5 = (TH1D*)f13.Get("55");
  TH1D* h6 = (TH1D*)f13.Get("56");
  cout<<"Entries h1 = "<<h1->GetEntries()<<" && percentage ="<<"100 "<<endl;
  cout<<"Entries h2 = "<<h2->GetEntries()<<" && percentage ="<<h2->GetEntries() *100/h1->GetEntries()<<endl;
  cout<<"Entries h3 = "<<h3->GetEntries()<<" && percentage ="<<h3->GetEntries() *100/h1->GetEntries()<<endl;
  cout<<"Entries h4 = "<<h4->GetEntries()<<" && percentage ="<<h4->GetEntries() *100/h1->GetEntries()<<endl;
  cout<<"Entries h5 = "<<h5->GetEntries()<<" && percentage ="<<h5->GetEntries() *100/h1->GetEntries()<<endl;
  cout<<"Entries h6 = "<<h6->GetEntries()<<" && percentage ="<<h6->GetEntries()*100/h1->GetEntries()<<endl;
  cout<<"Entries Sum= "<<(h6->GetEntries()+h5->GetEntries()+h4->GetEntries()+h3->GetEntries()+h2->GetEntries())/h1->GetEntries()<<endl;
}  

