import ROOT
ROOT.gROOT.SetBatch(True)

import sys

class makeCountingExperimentCards():

    def __init__(self, savepath, cardname):

        self.cardname = savepath + "/" + cardname #"CMS-HGG_mva_13TeV_datacard.txt"
        print self.cardname
        self.txtfile =  open(self.cardname, "w")

        #some lists
        self.processNames = []
        self.path = savepath


    def WriteBasicNum(self, nChannel, nSig, nBkg, nNuisance=0):

        if nChannel == -1:
            self.txtfile.write("imax *\n" )
        else:
            self.txtfile.write("imax {0}\n".format(nChannel) )

        if nSig == -1 and nBkg == -1:
            self.txtfile.write("jmax *\n" )
        else:
            self.txtfile.write("jmax {0}\n".format(nSig + nBkg - 1) )

        if nNuisance > 0:
            self.txtfile.write("kmax {0}\n".format(nNuisance) )
        else:
            self.txtfile.write("kmax *\n")

        self.txtfile.write("------------\n")

    def WriteBody(self):
        binList = list(self.yields.keys())
        self.txtfile.write(" bin " + " ".join(binList) + "\n")
        observationArray = []
        for i in range(len(binList)):
            observationArray.append("-1")

        self.txtfile.write("observation " + " ".join(observationArray) + "\n")
        self.txtfile.write("------------\n")


        self.txtfile.write("bin")
        for bin in binList:
            for i in range(len(self.processNames)):
                self.txtfile.write(" "+bin)
        self.txtfile.write("\n")

        self.txtfile.write("process")
        for bin in binList:
            for process in self.processNames: # order needs to be maintained!
                self.txtfile.write(" "+process)
        self.txtfile.write("\n")

        self.txtfile.write("process")
        for bin in binList:
            signalCount = 0 # negative
            backgroundCount = 1 # positive
            for process in self.processNames:
                if "HH" in process:
                    self.txtfile.write(" {}".format(signalCount))
                    signalCount -= 1
                else:
                    self.txtfile.write(" {}".format(backgroundCount))
                    backgroundCount += 1
        self.txtfile.write("\n")
        self.txtfile.write("rate")
        for bin in binList:
            for process in self.processNames:
                self.txtfile.write(" {:0.3f} ".format(self.yields[bin][process]))
        self.txtfile.write("\n")
        self.txtfile.write("------------\n")


    def WriteNuisance(self):
        # Nuisance list - for every nuisance parameter, a dictionary of numbers
        # or strings is provided, with the key being the name of the process
        # and the value being the value
        binList = list(self.yields.keys())

        for nuisance in self.nuisances.keys():
            self.txtfile.write(nuisance + " " + self.nuisances[nuisance]["type"])
            for bin in range(len(binList)):
                for process in self.processNames:
                    if process not in self.nuisances[nuisance]:
                        self.txtfile.write(" -")
                    else:
                        self.txtfile.write(" {}".format(self.nuisances[nuisance][process]))
            self.txtfile.write("\n")

    def WriteCard(self, yields, processes):
        self.processNames = processes
        self.WriteBasicNum(-1,-1,-1)
        self.yields = yields
        self.WriteBody()

        self.nuisances = {}
        self.nuisances["lumi_13TeV"] = {"type":"lnN", "HH_ggTauTau":1.025, "sm_higgs":1.025}
        self.nuisances["sm_higgs_xs"] = {"type":"lnN", "sm_higgs":"0.900/1.100"}

        self.WriteNuisance()

        self.txtfile.close()

