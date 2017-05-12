void parse() {}

void parse_stops(TString filename) {
  
  TFile *f = new TFile(filename + ".root","RECREATE");
  TTree *T = new TTree("ntuple","data from ascii file");
  std::string branchdesc = "export_date/C:export_time/C:no_course/I:arret_long/C:arret/C:arret_pays/C:arret_commune/C:arret_paysh/C:arret_rang/I:arret_charge_brut/I:arret_charge/D:arret_deviation/C:nb_descentes_brut/I:nb_descentes/D:nb_montee_brut/I:nb_montee/D:retard/I:h_depart_theo/C:h_depart_com/C:h_depart_real/C:h_entree_antip/C:deloc/C:reloc/C:dist_inter_sae/I:dist_inter_real/I:t_parcours_reel/I:t_parcours_theo/I:stop_creation/C";
  Long64_t nlines = T->ReadFile(filename,branchdesc.c_str(),';');
  printf(" found %lld points\n",nlines);
  T->Write();
}


void prune_tree(TString filename) {

  TFile *f = TFile::Open(filename);
   if (f == 0) {
     // if we cannot open the file, print an error message and return immediatly
     printf("Error: cannot open file");
     return;
   }

   // Create the tree reader and its data containers
   TTreeReader myReader("ntuple", f);
   TTreeReaderValue<char*> depart_real(myReader, "h_depart_real");
   
   // Loop over all entries of the TTree or TChain.
   while (myReader.Next()) {
      // Get the data from the current TTree entry by getting
     cout << *depart_real << endl;
   }

}
