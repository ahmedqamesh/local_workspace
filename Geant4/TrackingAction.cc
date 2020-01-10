#include "TrackingAction.hh"
#include "DetectorConstruction.hh"
#include "Run.hh"
#include "G4RunManager.hh"
#include "G4Positron.hh"
#include "G4PhysicalConstants.hh"
#include "G4TrackingManager.hh"
#include "HistoManager.hh"

#include "EventAction.hh"
#include "HistoManager.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"


//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

TrackingAction::TrackingAction(DetectorConstruction* det, EventAction* EA)
:G4UserTrackingAction(),fDetector(det),fEventAction(EA),fPhotoGamma(-1),fComptGamma(-1),
 fPhotoAuger(-1),fComptAuger(-1),fPixeGamma(-1),fPixeAuger(-1),fPhoto(-1),fcompton(-1),fundefined(-1),
 fIDdefined(false)
{ }

void TrackingAction::PreUserTrackingAction(const G4Track* track )
{
  //get Run
  Run* run = static_cast<Run*>(G4RunManager::GetRunManager()->GetNonConstCurrentRun());
  if (track->GetTrackID() == 1) {
 	for (G4int k=1; k<=fDetector->GetNbOfAbsor(); k++) {
  		if (k==fDetector->GetNbOfAbsor() ){
    		fXstartAbs[k] = fDetector->GetxstartAbs(k);
    		fXendAbs[k]   = fDetector->GetxendAbs(k);
    		fPrimaryCharge = track->GetDefinition()->GetPDGCharge();
  										}
									}
      	  	  	  	  	  	  	  }
  // Energy flow initialisation for primary particle
  if (track->GetTrackID() == 1) {
    G4int Idnow = 1;
    if (track->GetVolume() != fDetector->GetphysiWorld()) {
    // unique identificator of layer+absorber
      const G4VTouchable* touchable = track->GetTouchable();
      G4int absorNum = touchable->GetCopyNumber();
      G4int layerNum = touchable->GetReplicaNumber(1);
      Idnow = (fDetector->GetNbOfAbsor())*layerNum + absorNum;
    }

    G4double Eflow = track->GetKineticEnergy();
    if (track->GetDefinition() == G4Positron::Positron())
      Eflow += 2*electron_mass_c2;
    //flux artefact, if primary vertex is inside the calorimeter   
    for (G4int pl=1; pl<=Idnow; pl++) {run->SumEnergyFlow(pl, Eflow);}
  	 } else {
    run->AddSecondaryTrack(track);
  }

}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void TrackingAction::PostUserTrackingAction(const G4Track* track )
{
   G4AnalysisManager* analysisManager = G4AnalysisManager::Instance();
  //get Run
  Run* run = static_cast<Run*>(G4RunManager::GetRunManager()->GetNonConstCurrentRun());
  //get Track information of secondaries
	   G4ThreeVector pos   = track->GetPosition();
	   G4ThreeVector vert  = track->GetVertexPosition();
	   G4double charge     = track->GetDefinition()->GetPDGCharge();
	   G4int idx 		   = track->GetCreatorModelID();
	   G4String Model 	   = track->GetCreatorModelName();
	   G4double trackLength = track->GetTrackLength();
	   // Get the index of models
		fPhotoGamma = G4PhysicsModelCatalog::GetIndex("phot_fluo");
		fComptGamma = G4PhysicsModelCatalog::GetIndex("compt_fluo");
		fPhotoAuger = G4PhysicsModelCatalog::GetIndex("phot_auger");
		fComptAuger = G4PhysicsModelCatalog::GetIndex("compt_auger");
		fPixeGamma 	= G4PhysicsModelCatalog::GetIndex("gammaPIXE");
		fPixeAuger	= G4PhysicsModelCatalog::GetIndex("e-PIXE");
		fPhoto	= G4PhysicsModelCatalog::GetIndex("phot");
		fcompton	= G4PhysicsModelCatalog::GetIndex("compt");
		fundefined	= G4PhysicsModelCatalog::GetIndex("undefined");
		// Start looping over the absorbers
		for (G4int k=1; k<=fDetector->GetNbOfAbsor(); k++){
			   G4bool trans 	   = ((pos.x() >= fDetector->GetxendAbs(k)) && (vert.x() < fDetector->GetxendAbs(k)));
			   G4bool ref  		   = (pos.x() <= fDetector->GetxstartAbs(k));
			   G4bool notabs 	   = (trans || ref);
			   G4bool abs  = !notabs;
		// Record the kinetic energy for secondary particles
		if (track->GetParentID() == 1 && charge != 0.) {
			analysisManager->FillH1(35,track->GetKineticEnergy());
			if (ref) analysisManager->FillH1(36,track->GetKineticEnergy());
			if(trans) {
			  analysisManager->FillH1(37,track->GetKineticEnergy());
			  if(idx == fPhoto) analysisManager->FillH1(41,track->GetKineticEnergy());
			  if(idx == fcompton) analysisManager->FillH1(42,track->GetKineticEnergy());
			  if(idx == fPhotoAuger || idx == fComptAuger) analysisManager->FillH1(34,track->GetKineticEnergy());
			  if(idx == fPixeAuger)analysisManager->FillH1(44,track->GetKineticEnergy());
			}
			if (abs )analysisManager->FillH1(38,track->GetKineticEnergy());
	  //G4cout<<"vert.x() = "<<vert.x()<<G4endl;
	  analysisManager->FillH1(40,vert.x());
	  analysisManager->FillH1(39,trackLength);
		}







   //transmitted + reflected particles counter
	G4int flag = 0;
	if (charge == fPrimaryCharge)  flag = 1;
	if (track->GetTrackID() == 1) flag = 2;
	if (trans) fEventAction->SetTransmitFlag(flag);
	if (ref)  fEventAction->SetReflectFlag(flag);




	// Get Info from the last Layer
	if (k==fDetector->GetNbOfAbsor()){
  G4ThreeVector position = track->GetPosition();
  G4ThreeVector vertex   = track->GetVertexPosition();
   	G4bool transmit = ((position.x() >= fXendAbs[k]) && (vertex.x() < fXendAbs[k]));
   	G4bool reflect  =  (position.x() <= fXstartAbs[k]);
   	G4bool notabsor= (transmit || reflect);

 //energy spectrum at exit
  	G4bool charged  = (charge != 0.);
  	G4bool neutral = !charged;
  	G4int id = 0;  
         if (transmit && charged) id = 31;
    else if (transmit && neutral) id = 32;
  	else if (reflect  && charged) id = 33;
  	else if (reflect && neutral) id = 34;
  //if (track->GetKineticEnergy() < 0.15 && track->GetKineticEnergy()> 0) G4cout << "very low energy " <<track->GetKineticEnergy()<<"=========================="<<track->GetTrackID()<<G4endl;
 	if (id>0) analysisManager->FillH1(id, track->GetKineticEnergy());

    //projected angles distribution at exit
 	G4ThreeVector direction = track->GetMomentumDirection();
 	id = 0;
 	if (trans && charge != 0.) id = 45;
 	else if (ref  && charge != 0.) id = 46;
 	if (id>0) {
 		if (direction.x() != 0.0) {
 		G4double tet = std::atan(direction.y()/std::fabs(direction.x()));
 		analysisManager->FillH1(id,tet);
 		if (trans && (flag == 2)) run->AddMscProjTheta(tet);
 		tet = std::atan(direction.z()/std::fabs(direction.x()));
 		analysisManager->FillH1(id,tet);
 		if (trans && (flag == 2)) run->AddMscProjTheta(tet);
 		 }
 	   }

 	//projected position and radius at exit
  id = 0;   
  if (transmit && charged) id = 47;
 //if (transmit && neutral) id = 47;
  if (id>0) {
    G4double y = position.y(), z = position.z();
    G4double r = std::sqrt(y*y + z*z);
   analysisManager->FillH1(id,   y);
   analysisManager->FillH1(id,   z);
   analysisManager->FillH1(id+1, r); //This will fill number 48

  }
  //x-vertex of charged secondaries
  if ((track->GetParentID() == 1) && charged) {
    G4double xVertex = (track->GetVertexPosition()).x();
   analysisManager->FillH1(49, xVertex);
   if (notabsor) analysisManager->FillH1(50, xVertex); 
  	  	  	  }
	}//end of If statement For K = NbAbsorbers
  }//end of For Loop of Nbabsorbers
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

