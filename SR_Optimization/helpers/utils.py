import numpy
import math

def find_nearest(array, value):
    val = numpy.ones_like(array)*value
    idx = (numpy.abs(array-val)).argmin()
    return array[idx], idx

def calculate_cut_values(n_points, mva_scores, n_quantiles = 1000):
    """
    Select n_points evenly spaced cuts in signal efficiency.
    """
    map = {}
    quantiles_to_mva_map = quantiles_to_mva_score(n_quantiles, mva_scores)
    quantiles = list(quantiles_to_mva_map.keys())
    for i in range(n_points):
        fraction = float(i) / float(n_points)
        quantile, idx = find_nearest(quantiles, fraction)
        map[i] = quantiles_to_mva_map[quantile]
    return map

def quantiles_to_mva_score(n_quantiles, mva_scores):
    sorted_mva = numpy.sort(mva_scores)
    map = {}

    for i in range(n_quantiles):
        idx = int((float(i+1) / float(n_quantiles)) * len(sorted_mva)) - 1
        quantile = float(i) / float(n_quantiles)
        mva_score = sorted_mva[idx]
        map[quantile] = mva_score

    return map

def calculate_za(signal_events, resonant_background_events, background_events, data_events, options):
    """
    Fits signal_events, resonant_background_events, background_events, and data_events separately in n_bins.
    Calculates a metric with combine and returns results
    """

    results = {}

    idx = 0
    results["Z_A_combined"] = 0
    for sig, res_bkg, bkg, data in zip(signal_events, resonant_background_events, background_events, data_events):
        idx += 1
        #sig_model = make_resonant_model(sig, options["resonant"])
        #res_bkg_model = make_resonant_model(res_bkg, options["resonant"])
        #bkg_model = make_background_model(bkg, options["non_resonant"])
        #data_model = make_background_model(bkg, options["non_resonant"])

        n_sig = sig["weight"].loc[sig["ggMass"].between(122, 128, inclusive=True)].sum()
        n_res_bkg = res_bkg["weight"].loc[res_bkg["ggMass"].between(122, 128, inclusive=True)].sum()
        n_bkg = bkg["weight"].sum() * (6./70.) # scale by [122,128] / [100, 120] U [130, 180]

        za = Z_A(n_sig, n_res_bkg + n_bkg)

        results["Bin_%d" % idx] = {
            "n_signal" : n_sig,
            "n_resonant_background" : n_res_bkg,
            "n_bkg" : n_bkg,
            "Z_A" : za
        }
        results["Z_A_combined"] += za**2

    results["Z_A_combined"] = math.sqrt(results["Z_A_combined"])
    return results

def Z_A(s, b):
  if s <= 0:
    return 0
  if b <= 0:
    return 0
  q1 = 2 * ( ((s+b) * math.log(1 + (s/b) )) - s)
  if q1 <= 0:
    return 0
  else:
    return math.sqrt(q1)
