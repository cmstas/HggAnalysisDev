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

class ModelHelper():
    """
    Class to make parametric models: exponential for non-resonant background
    and double crystal ball for resonant background
    """

    def __init__(self, **kwargs):
        self.events = kwargs.get("events")
        self.model = kwargs.get("model")
        self.tag = kwargs.get("tag")
        self.output_dir = kwargs.get("output_dir")
        self.resonant = kwargs.get("resonant")

    def run(self):
        self.setup()
        self.fit_model()
        self.assess()

    def setup(self):
        if os.path.exists(self.output_dir):
            os.system("rm -rf %s" % (self.output_dir + "/*" + self.tag + "*"))
        else:
            os.system("mkdir %s" % self.output_dir)

        # Initialize workspace
        self.w = ROOT.RooWorkspace("w")
        self.rooVar = "mgg"

        # Initialize and fill histogram
        self.h = ROOT.TH1F("h_mgg", "h_mgg", 320, 100, 180)
        self.h.Sumw2()
        root_numpy.fill_hist(self.h, self.events["ggMass"], weights = self.events["weight"])
                
        # Convert to RooDataHist
        self.d = ROOT.RooDataHist("d_mgg_" + self.tag, "", ROOT.RooArgList(self.w.var(self.rooVar)), self.h, 1)
        self.norm = self.d.sumEntries()
        self.rooVarNorm = ROOT.RooRealVar(self.tag + "_norm", "", self.norm)
        self.pdf = ROOT.RooExtendPdf(self.tag + "_pdf", "", self.w.pdf(self.tag), self.rooVarNorm)

        if not self.resonant:
            self.w.var(self.rooVar).setRange("SL", 100, 120)
            self.w.var(self.rooVar).setRange("SU", 130, 180)
        
        return

    def fit_model(self):
        if self.model == "DCB":
            w.factory("DoubleCB:" + self.tag + "(" + self.rooVar + ", mean_" + self.tag + "[125,123,127], sigma_" + self.tag + "[1,0.5,5], a1_" + self.tag+ "[1,0.1,10], n1_" + self.tag + "[1,0.1,10], a2_" + self.tag + "[1,0.1,10], n2_" + self.tag + "[1,0.1,10]")
            self.w.pdf(self.tag + "_pdf").fitTo(d_mgg, ROOT.RooFit.PrintLevel(-1))

        elif self.model == "Exp":
            w.factory("Exponential:" + self.tag + "(" + self.rooVar ", tau[-0.027, -0.1, -0.01])")
            self.w.pdf(self.tag + "_pdf").fitTo(d_mgg, ROOT.RooFit.Range("SL,SU"), ROOT.RooFit.Extended(True), ROOT.RooFit.PrintLevel(-1))        

        getattr(self.w, "import")(self.rooVarNorm)
        getattr(self.w, "import")(self.pdf)

        return

    def assess(self):
        self.norm_full = self.w.pdf(self.tag

        return

    def make_plots(self):
         
