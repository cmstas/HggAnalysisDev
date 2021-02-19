import os

import ROOT
ROOT.gROOT.SetBatch(True)
import root_numpy

from tdrStyle import *
setTDRStyle()

ROOT.gSystem.AddIncludePath("-I$CMSSW_BASE/src/ ")
ROOT.gSystem.Load("$CMSSW_BASE/lib/slc7_amd64_gcc700/libHiggsAnalysisCombinedLimit.so")
ROOT.gSystem.AddIncludePath("-I$ROOFITSYS/include")
ROOT.gSystem.AddIncludePath("-Iinclude/")
ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.DataHandling)
ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.ObjectHandling)

from helpers import model_helper

class CombineHelper():
    """
    Class to create models from m_gg distributions of signal/resonant_bkg/bkg MC/data events
    for a specified number of bins.
    Next runs combine and extracts a specified metric (significance, upper limit, etc.)
    """

    def __init__(self, **kwargs):
        self.options = kwargs.get("options")
        self.signal_events = kwargs.get("signal_events") 
        self.resonant_background_events = kwargs.get("resonant_background_events")
        self.background_events = kwargs.get("background_events")
        self.data_events = kwargs.get("data_events")
        self.output_dir = kwargs.get("output_dir")
        self.output_tag = kwargs.get("output_tag")

    def run(self):
        self.setup()
        self.make_models()
        self.run_combine()
        self.summarize()

    def setup(self):
        self.info = {
            "signal" : {
                "fit" : self.options["resonant"]["fit"],
                "resonant" : True,
                "models" : [],
                "events" : self.signal_events
            },
            "resonant_bkg" : {
                "fit" : self.options["resonant"]["fit"],
                "resonant" : True,
                "models" : [],
                "events" : self.resonant_background_events
            },
            "bkg_MC" : {
                "fit" : self.options["non_resonant"]["fit"],
                "resonant" : False,
                "models" : [],
                "events" : self.background_events
            },
            "data" : {
                "fit" : self.options["non_resonant"]["fit"],
                "resonant" : False,
                "models" : [],
                "events" : self.data_events
            }
        }
        return

    def make_models(self):
        for event_type, info in self.info.items():
            for i in range(self.options["n_bins"]):
                helper = model_helper.ModelHelper(
                    events = info["events"][i],
                    model = info["fit"],
                    tag = event_type + "Bin%d" % i,
                    output_dir = self.output_dir,
                    resonant = info["resonant"]
                )
                helper.run()
                info["models"].append(helper.model_file)

    def run_combine(self):
        return

    def summarize(self):
        return

    def get_results(self):
        return { "upper_limit" : 0 }

