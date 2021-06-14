# Cross section
xs_hh = 31.05 # https://arxiv.org/pdf/2011.12373.pdf

xs_tthh = 0.775 # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHWGHH#tthh
xs_zhh = 0.363 # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHWGHH#hhZ
xs_wminus_hh = 0.173 # W-
xs_wplus_hh = 0.329 # W+
xs_whh = xs_wminus_hh + xs_wplus_hh
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

# ggbb
xs_hh_ggbb = xs_hh * bf_hgg * bf_hbb * 2

# ggWW
xs_hh_ggWW = xs_hh * bf_hgg * bf_hww * 2
xs_hh_ggWW_dileptonic = xs_hh_ggWW * (bf_wlnu**2)
xs_hh_ggWW_semileptonic = xs_hh_ggWW * bf_wlnu * bf_wqq * 2

# ggZZ
xs_hh_ggZZ = xs_hh * bf_hgg * bf_hzz * 2

# ttHH -> ggbb
xs_tthh_ggbb = xs_tthh * bf_hgg * bf_hbb * 2
xs_tthh_ggWW = xs_tthh * bf_hgg * bf_hww * 2
xs_tthh_ggTauTau = xs_tthh * bf_hgg * bf_htautau * 2
xs_whh_ggbb = xs_whh * bf_hgg * bf_hbb * 2
xs_whh_ggWW = xs_whh * bf_hgg * bf_hww * 2
xs_whh_ggTauTau = xs_whh * bf_hgg * bf_htautau * 2
xs_zhh_ggbb = xs_zhh * bf_hgg * bf_hbb * 2
xs_zhh_ggWW = xs_zhh * bf_hgg * bf_hww * 2
xs_zhh_ggTauTau = xs_zhh * bf_hgg * bf_htautau * 2


print("Cross section for HH->ggTauTau: %.6f" % (xs_hh_ggTauTau))
print("Cross section for HH->ggbb: %.6f" % (xs_hh_ggbb))
print("Cross section for HH->ggWW: (dileptonic): %.6f" % (xs_hh_ggWW_dileptonic))
print("Cross section for HH->ggWW: (semileptonic): %.6f" % (xs_hh_ggWW_semileptonic))
print("Cross section for HH->ggZZ: %.6f" % (xs_hh_ggZZ))
print("Cross section for ttHH->ggbb: %.6f" % (xs_tthh_ggbb))
print("Cross section for ttHH->ggWW: %.6f" % (xs_tthh_ggWW))
print("Cross section for ttHH->ggTauTau: %.6f" % (xs_tthh_ggTauTau))
print("Cross section for WHH->ggbb: %.6f" % (xs_whh_ggbb))
print("Cross section for WHH->ggWW: %.6f" % (xs_whh_ggWW))
print("Cross section for WHH->ggTauTau: %.6f" % (xs_whh_ggTauTau))
print("Cross section for ZHH->ggbb: %.6f" % (xs_zhh_ggbb))
print("Cross section for ZHH->ggWW: %.6f" % (xs_zhh_ggWW))
print("Cross section for ZHH->ggTauTau: %.6f" % (xs_zhh_ggTauTau))

