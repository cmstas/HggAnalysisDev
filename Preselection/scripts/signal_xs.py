# Cross section
xs_hh = 31.05 # https://arxiv.org/pdf/2011.12373.pdf
xs_vbf_hh = 1.726  # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHWGHH?redirectedfrom=LHCPhysics.LHCHXSWGHH#Current_recommendations_for_di_H
xs_tthh = 0.775

# Branching fractions: from Table 11.3 of https://pdg.lbl.gov/2016/reviews/rpp2016-rev-higgs-boson.pdf
bf_hgg = 0.00227
bf_hzz = 0.0262
bf_hbb = 0.584
bf_hww = 0.214
bf_htautau = 0.0627

bf_wlnu = 0.317
bf_wqq = 0.683

# ggTauTau
xs_hh_ggTauTau = xs_hh * bf_hgg * bf_htautau * 2
xs_vbf_hh_ggTauTau = xs_vbf_hh * bf_hgg * bf_htautau * 2

# ggbb
xs_hh_ggbb = xs_hh * bf_hgg * bf_hbb * 2
xs_vbf_hh_ggbb = xs_vbf_hh * bf_hgg * bf_hbb * 2
xs_tthh_ggbb = xs_tthh * bf_hgg * bf_hbb * 2
xs_tthh_ggtt = xs_tthh * bf_hgg * bf_htautau * 2
xs_tthh_ggWW = xs_tthh * bf_hgg * bf_hww * 2

# ggWW
xs_hh_ggWW = xs_hh * bf_hgg * bf_hww * 2
xs_vbf_hh_ggWW = xs_vbf_hh * bf_hgg * bf_hww * 2
xs_hh_ggWW_dileptonic = xs_hh_ggWW * (bf_wlnu**2)
xs_vbf_hh_ggWW_dileptonic = xs_vbf_hh_ggWW * (bf_wlnu**2)
xs_hh_ggWW_semileptonic = xs_hh_ggWW * bf_wlnu * bf_wqq * 2
xs_vbf_hh_ggWW_semileptonic = xs_vbf_hh_ggWW * bf_wlnu * bf_wqq * 2

# ggZZ
xs_hh_ggZZ = xs_hh * bf_hgg * bf_hzz * 2
xs_vbf_hh_ggZZ = xs_vbf_hh * bf_hgg * bf_hzz * 2

print("Cross section for ttHH->ggbb: %.6f" % (xs_tthh_ggbb))
print("Cross section for ttHH->ggXX: %.6f" % (xs_tthh_ggbb+xs_tthh_ggtt+xs_tthh_ggWW))
print("BR for HH->ggbb: %.6f" % (bf_hgg * bf_hbb * 2))
print("BR for HH->ggww: %.6f" % (bf_hgg * bf_hww * 2))
print("BR for HH->ggtautau: %.6f" % (bf_hgg * bf_htautau * 2))

print("Scale factor for HH->ggww: %.6f" % (bf_hww /bf_hbb))
print("Scale factor for HH->ggtautau: %.6f" % (bf_htautau/bf_hbb))

print("Cross section for ggF HH->ggTauTau: %.6f" % (xs_hh_ggTauTau))
print("Cross section for ggF HH->ggbb: %.6f" % (xs_hh_ggbb))
print("Cross section for ggF HH->ggWW: (dileptonic): %.6f" % (xs_hh_ggWW_dileptonic))
print("Cross section for ggF HH->ggWW: (semileptonic): %.6f" % (xs_hh_ggWW_semileptonic))
print("Cross section for ggF HH->ggZZ: %.6f" % (xs_hh_ggZZ))

print("Cross section for VBF HH->ggTauTau: %.6f" % (xs_vbf_hh_ggTauTau))
print("Cross section for VBF HH->ggbb: %.6f" % (xs_vbf_hh_ggbb))
print("Cross section for VBF HH->ggWW: (dileptonic): %.6f" % (xs_vbf_hh_ggWW_dileptonic))
print("Cross section for VBF HH->ggWW: (semileptonic): %.6f" % (xs_vbf_hh_ggWW_semileptonic))
print("Cross section for VBF HH->ggZZ: %.6f" % (xs_vbf_hh_ggZZ))


