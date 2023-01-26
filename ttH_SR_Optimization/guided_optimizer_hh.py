import os, sys
import getpass
import multiprocessing
from json import JSONEncoder
import json
import math

# Disable these, don't really need them 
#import tensorflow
#import keras
import xgboost
import pandas
from sklearn.model_selection import train_test_split

import numpy

import ROOT
import root_numpy

from scanClass import scanClass
from makeModels import makeModel
from cardMaker import makeCards

process_dict = { ##TODO Update this to match the DF campaign you are using!
    # Var XChecks  
    # "data" : [14],
    # "ttHH" : [11,12,13],
    # "ggHH" : [1, 2],
    # "bkg" : [0, 3, 4, 5, 6, 15, 16, 17, 18, 19, 20],
    # "sm_higgs" : [7, 8, 9, 10]

    #Ian Spike check 
    # 20 = 2HDM 300
    # 19 = 2HDM 250
    "data" : [0],
    "ttHH" : [19],#[2,3,4],
    # "ggHH" : [],
    "bkg" : [8,9,10,11,12,13,14,15,16,17,18],
    "sm_higgs" : [1,5,6,7,2,3,4],

    #c2=6 training
    "data" : [0],
    "ttHH" : [36],
    # "ggHH" : [],
    "bkg" : [-99,13,14,15,16,17,18],
    "sm_higgs" : [1,2,5,6,7,19,20,21,22],

}


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

class Guided_Optimizer():
    def __init__(self, **kwargs):
        self.input  =   kwargs.get('input')
        self.tag    =   kwargs.get('tag', '')
        self.channel = "FCNC_Hadronic" if "Hadronic" in self.input else "FCNC_Leptonic"
        self.diagnostic_mode = kwargs.get('diagnostic_mode', False)

        self.mvas   =   kwargs.get('mvas', { "1d" : ["mva_score"], "2d" : ["mva_smhiggs_score", "mva_nonres_score"] }) 
        self.n_bins =   kwargs.get('n_bins', [1, 2, 3, 4]) 
        self.strategies = kwargs.get('strategies', ['random', 'guided'])

        self.nCores = kwargs.get('nCores', 12)

        self.verbose = kwargs.get('verbose', True)

        self.nrb_choice = kwargs.get('nrb_choice', 'bkg')
        self.combineOption = kwargs.get('combineOption', 'AsymptoticLimits -m 125 ')
        self.sm_higgs_unc  = kwargs.get('sm_higgs_unc', 0.4)

        self.coupling = kwargs.get('coupling')
        if self.coupling == "ttH":
            self.signal = ["ttH"]
        else:
            self.signal =   kwargs.get('signal', ['FCNC_%s' % self.coupling])
        self.resonant_bkgs = kwargs.get('resonant_bkgs', ['sm_higgs'])
        if self.coupling == "ttH":
            self.resonant_bkgs = ['sm_higgs']

        if self.coupling == "HH":
            self.signal = ["ggHH"]
        if self.coupling == "ttHH":
            self.signal = ["ttHH"]
        #if "Leptonic" in kwargs.get('channel'):
            #    self.resonant_bkgs = ['sm_higgs_nottHnoggH']

        self.points_per_epoch = kwargs.get('points_per_epoch', 200)
        self.initial_points = kwargs.get('initial_points', 48)
        self.n_epochs = kwargs.get('n_epochs', -1) # how many epochs of optimization to run (-1 means run until convergence)

        self.pt_selection = kwargs.get('pt_selection', '')

        self.mva = kwargs.get('mva', 'bdt')
        self.dnn_config = kwargs.get('dnn_config', {
                                "dropout" : 0.0,
                                "n_nodes" : 128,
                                "n_layers" : 5,
                                "batch_norm" : False,
                                "activation" : "relu",
                                "learning_rate" : 0.00001,
                                "loss" : "mean_absolute_error",
                                "batch_size" : 1000,
                            })

        self.bdt_config = kwargs.get('bdt_config', {
                                'max_depth': 10,
                                'eta': 0.2,
                                'objective': 'reg:linear',
                                'subsample': 1.0,
                                'colsample_bytree': 1.0,
                                'nthread' : 12, 
                            })

        user = getpass.getuser() 
        current_dir = os.getcwd()
        self.modelpath = current_dir + "/models/" + self.tag
        self.plotpath = ("/home/users/%s/public_html/Binning/" % user) + self.tag
        self.scanConfig = kwargs.get('scanConfig', { "tag" : self.channel,
                                                     "filename" : self.input,
                                                     "selection" : "",
                                                     "sigName" : self.signal[0] + "_hgg",
                                                     "var" : "mass",
                                                     "weightVar" : "weight_central",
                                                     "modelpath" : self.modelpath,
                                                     "plotpath" : self.plotpath, 
                                                     "combineEnv" : current_dir + "/CMSSW_10_2_13/src",
                                                    })

        # Setup
        f = ROOT.TFile(self.input)
        self.tree = f.Get("t")
    
        self.n_points = self.points_per_epoch


    def optimize(self): 
        self.results = {}
        for dim, mvas in self.mvas.items():
            self.results[dim] = {}
            for n_bin in self.n_bins:
                self.results[dim][n_bin] = {}
                for strategy in self.strategies:
                    self.find_optimal_binning(dim, mvas, n_bin, strategy)

        # save results
        outfile = "optimization_results/guided_optimizer_results_%s_%s_%s.json" % (self.coupling, self.channel, self.tag)
        with open(outfile, "w") as f_out:
            json.dump(self.results, f_out, cls = NumpyArrayEncoder, sort_keys = True, indent = 4)


    def find_optimal_binning(self, dim, mvas, n_bin, strategy): # find optimal binning for len(mvas)-D optimization with n_bin SRs
        if self.verbose:
            print("[GUIDED OPTIMIZER] Finding optimal binning for %s optimization in mva scores: %s with n_bin = %d, and %s optimiziation strategy" % (dim, mvas, n_bin, strategy))
        
        self.iteration_ctr = 0
        self.results[dim][n_bin][strategy] = {
            "X" : [], # points actually tried
            "y" : [], # limits for these points
            "exp_lim" : [], # dict with idx, exp_lim (+/-1sigma), selection
            "eff" : [], # acceptance rate vs. epoch (1 for random sampling)
            "sample_mean" : [], # mean value of limit for sampled points vs. epoch
            "sample_std" : [], # std ""
            "sample_best" : [], # best limit for sampled points vs. epoch
            "accuracy" : [], # dnn accuracy vs. epoch
        }
        
        self.n_bad_epochs = 0

        initial_results = self.initialize(mvas, n_bin)
        self.update_results(dim, n_bin, strategy, initial_results)

        self.converged = False
        if self.diagnostic_mode:
            return

        while not self.converged:
            if strategy == "guided":
                accuracy = self.train_mva(self.results[dim][n_bin][strategy]["X"], self.results[dim][n_bin][strategy]["y"])
            elif strategy == "random":
                accuracy = 0

            results = self.sample(mvas, n_bin, strategy)
            results["accuracy"] = accuracy
            self.update_results(dim, n_bin, strategy, results) 

            self.check_convergence(self.results[dim][n_bin][strategy])
           
            self.reset_mva(mvas, n_bin) 

    def reset_mva(self, mvas, n_bin):
        if self.mva == "dnn":
            self.initialize_dnn(n_bin * len(mvas)) # reset dnn (so we start out with a fresh training)
        if self.mva == "bdt":
            self.initialize_bdt(n_bin * len(mvas))

    def check_convergence(self, results): # if we go N epochs without improving by X%, we are converged
        N = 50 # number of early stopping rounds
        X = 0.01

        if self.n_epochs > 0 and self.iteration_ctr >= self.n_epochs: # max limit on n_epochs
            self.converged = True
            return

        if len(results["sample_best"]) <= 1: # need at least 2 optimization epochs to start asking about convergence
            self.converged = False
            return

        best_limit = min(results["sample_best"][:-1]) # find best limit from all previous epochs (not this one)

        if (results["sample_best"][-1] * (1 + X)) <= best_limit:
            self.converged = False # not converged bc we improved by at least X%
        else:
            self.n_bad_epochs += 1
            if self.n_bad_epochs >= N:
                self.converged = True
            else:
                self.converged = False

    def update_results(self, dim, n_bin, strategy, results):
        if not results:
            return
        
        for field in ["X", "y", "exp_lim"]:
            if len(self.results[dim][n_bin][strategy][field]) == 0:
                self.results[dim][n_bin][strategy][field] = numpy.array(results[field])
            else:
                self.results[dim][n_bin][strategy][field] = numpy.concatenate([self.results[dim][n_bin][strategy][field], numpy.array(results[field])])
        
        for field in ["eff", "sample_mean", "sample_std", "sample_best", "accuracy"]:
            self.results[dim][n_bin][strategy][field].append(results[field])

        self.current_best_lim = min(self.results[dim][n_bin][strategy]["sample_best"])

        self.iteration_ctr += 1

        if self.verbose:
            print("[GUIDED OPTIMIZER] Finished optimization epoch %d, for %s optimization with %d bins and %s optimization strategy" % (self.iteration_ctr, dim, n_bin, strategy))
            print("[GUIDED OPTIMIZER] Summary of results so far:")
            print("[GUIDED OPTIMIZER] Mean value of sampled points vs. epoch: ", self.results[dim][n_bin][strategy]["sample_mean"])
            print("[GUIDED OPTIMIZER] Best value of sampled points vs. epoch: ", self.results[dim][n_bin][strategy]["sample_best"])
            print("[GUIDED OPTIMIZER] Efficiency of proposed points vs. epoch: ", self.results[dim][n_bin][strategy]["eff"])
            print("[GUIDED OPTIMIZER] DNN Accuracy vs. epoch: ", self.results[dim][n_bin][strategy]["accuracy"])



    def initialize(self, mvas, n_bin): # randomly sample initial_points points to get initial training/testing set
        # Set up scanClass
        self.scanConfig["modelpath"] = self.modelpath + "_%dd_%dbin_%s_%s/" % (len(mvas), n_bin, self.channel, self.coupling)
        self.scanConfig["plotpath"] = self.plotpath + "_%dd_%dbin_%s_%s/" % (len(mvas), n_bin, self.channel, self.coupling)
        self.scanner = scanClass(self.scanConfig)
        self.scanner.cleanDir()

        # Calculate quantiles <-> mva scores
        if self.verbose:
            print("[GUIDED OPTIMIZER] Calculating quantiles to mva score function")
    
        self.quantiles = {}
        for mva in mvas:
            scores, quantiles = self.scanner.quantiles_to_mva_score(5000, mva, self.base_selection() + "&&" + self.process_selection(self.signal[0]))
            self.quantiles[mva] = { "scores" : scores, "quantiles" : quantiles }

        # Set up DNN
        self.initialize_mva(n_bin * len(mvas))

        # sample initial points and calculate limits
        X, acc = self.generate_cut_combos(self.initial_points, mvas, n_bin, mode = 'random')
        exp_limits = self.calculate_expected_limits(X, mvas, n_bin)
        #y = exp_limits[:]["exp_lim"][0]
        y = []
        X_ = []
        for lim in exp_limits:
            X_.append(lim["x"])
            y.append(lim["exp_lim"][0])

        if len(y) == 0:
            return {}

        results = {
            "X" : X_,
            "y" : y,
            "exp_lim" : exp_limits,
            "eff" : 1,
            "sample_mean" : numpy.mean(y),
            "sample_std"  : numpy.std(y),
            "sample_best" : min(y),
            "accuracy" : 0,
        }

        return results

    def initialize_mva(self, n_cuts):
        if self.mva == "dnn":
            self.initialize_dnn(n_cuts)
        elif self.mva == "bdt":
            self.initialize_bdt(n_cuts)

    def initialize_bdt(self, n_cuts):
        self.bdt = self.bdt_regressor(n_cuts, self.bdt_config)

    def initialize_dnn(self, n_cuts):
        self.model = self.mlp(n_cuts, self.dnn_config)

    def bdt_regressor(self, n_cuts, config):
        return xgboost.XGBRegressor()

    # disable this function so people don't need to fight with installing tensorflow/keras within CMSSW
    def mlp(self, n_cuts, config):
        """
        dropout = config["dropout"]
        n_nodes = config["n_nodes"]
        n_layers = config["n_layers"]
        batch_norm = config["batch_norm"]
        learning_rate = config["learning_rate"]
        activation = config["activation"]
        loss = config["loss"]

        input_global = keras.layers.Input(shape=(n_cuts,), name = 'input_global')
        dense = input_global
        for i in range(n_layers):
            dense = keras.layers.Dense(n_nodes, activation = activation, kernel_initializer = 'lecun_uniform', name = 'dense_%d' % i)(dense)
            if dropout > 0:
                dense = keras.layers.Dropout(rate = dropout, name = 'dense_dropout_%d' % i)(dense)
            if batch_norm:
                dense = keras.layers.BatchNormalization(name = 'dense_batchnorm_%d' % i)(dense)

        output = keras.layers.Dense(1, kernel_initializer = 'lecun_uniform', name = 'output')(dense)


        model = keras.models.Model(inputs = [input_global], outputs = [output])
        optimizer = keras.optimizers.Adam(lr = learning_rate)
        model.compile(optimizer = 'adam', loss = loss, metrics = ['mae'])
    
        if self.verbose:
            print("[GUIDED OPTIMIZER] DNN Model Summary:", model.summary())
            print("[GUIDED OPTIMIZER] DNN Config:", config)

        return model
        """
        return None

    def train_mva(self, X, y):
        if self.mva == "dnn":
            return self.train_dnn(X, y)
        elif self.mva == "bdt":
            return self.train_bdt(X, y)

    def train_bdt(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size = 0.8)

        X_train = pandas.DataFrame(data = X_train)
        X_test = pandas.DataFrame(data = X_test)

        eval_list = [(X_test, y_test)]
        self.bdt.fit(X_train, y_train, early_stopping_rounds=5, eval_metric='mae', eval_set = eval_list)

        pred_test = self.bdt.predict(X_test)

        percent_error = (pred_test - y_test) / y_test
        percent_error_mean = numpy.mean(percent_error)
        percent_error_std  = numpy.std(percent_error)

        self.percent_error = numpy.sqrt(numpy.mean(percent_error**2)) # just use rms 

        if self.verbose:
            print("[GUIDED OPTIMIZER] Finished training BDT with error %.3f +/- %.3f" % (percent_error_mean, percent_error_std))

        return percent_error_std 
        
    def train_dnn(self, X, y): # train dnn with early stopping
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size = 0.8)

        train_more = True
        best_val_loss = 999
        ticker = 0
        while train_more:
            results = self.model.fit([X_train], y_train, batch_size = self.dnn_config["batch_size"], validation_data = (X_test, y_test), epochs = 1)
            val_loss = results.history['val_loss'][0]
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                ticker = 0
            else:
                ticker += 1
            if ticker >= 15:
                train_more = False

        pred_test = self.model.predict([X_test], batch_size = 10**5)[:,0]
        percent_error = (pred_test - y_test) / y_test

        percent_error_mean = numpy.mean(percent_error)
        percent_error_std  = numpy.std(percent_error)

        self.percent_error = numpy.sqrt(numpy.mean(percent_error**2)) # just use rms 

        if self.verbose:
            print("[GUIDED OPTIMIZER] Finished training DNN with error %.3f +/- %.3f" % (percent_error_mean, percent_error_std)) 
        
        return percent_error_std


    def sample(self, mvas, n_bin, strategy):
        X, eff = self.generate_cut_combos(self.n_points, mvas, n_bin, strategy)

        exp_limits = self.calculate_expected_limits(X, mvas, n_bin)

        X_ = []
        y = []
        for lim in exp_limits:
            X_.append(lim["x"])
            y.append(lim["exp_lim"][0])

        sample_mean = numpy.mean(y)
        sample_std  = numpy.std(y)
        sample_best = min(y)

        results = {
            "X" : X_,
            "y" : y, 
            "exp_lim" : exp_limits,
            "eff" : eff,
            "sample_mean" : sample_mean, 
            "sample_std" : sample_std,
            "sample_best" : sample_best
         }

        return results


    def generate_cut_combos(self, N_combos, mvas, n_bin, mode):
        if mode == 'random':
            X = self.generate_random_cut_combos(N_combos, mvas, n_bin)
            return X, 1.0

        elif mode == 'guided':
            X = []

            n_total = 0
            while len(X) < N_combos:
                n_total += N_combos
                X += self.subsample(self.generate_random_cut_combos(N_combos, mvas, n_bin))          
                
                if self.verbose:
                    print("[GUIDED OPTIMIZER] Subsampling: %d accepted points with %d total points tried (%.3f acceptance rate)" % (len(X), n_total, float(len(X))/float(n_total)))


            eff = float(len(X))/float(n_total)

            return X, eff

        else:
            print("[GUIDED_OPTIMIZER] sample mode: %s is not supported!" % mode)
            sys.exit(1)

    def reasonable_effs(self, effs):
        if effs[0] < 0.1:
            return False # don't accept SRs with signal eff less than 5%
        #if effs[-1] > 0.9: # don't accept SRs with the lowest signal eff defined by a cut that has more than 80% efficiency on signal
        #    return False
        if len(effs) > 1:
            for i in range(len(effs)-1):
                if (effs[i+1] - effs[i]) < 0.1:
                    return False
        return True

    def generate_effs(self, n):
        effs = []
        for i in range(n):
            if len(effs) == 0:
                effs.append(numpy.random.uniform(0.1, 1.0 - (i*0.1)))
            else:
                effs.append(numpy.random.uniform(effs[-1] + 0.1, 1.0 - ((n-i) * 0.1)))
        return effs

    def generate_effs_2d(self, n):
        min_eff = 0.1

        effs_x = []
        effs_y = []

        for i in range(n):
            mag = numpy.random.uniform(0.1, 0.9 - (n*0.1))

            angle = numpy.random.uniform(0.0, 3.14159 / 2.) # enforcing that both mvas must get looser in ensuing cuts (i.e. can't form an SR by loosening one mva but tightening another)

            delta_x = max(0.01, mag * math.cos(angle)) # also enforce that both dimensions must loosen by at least 1% in signal eff
            delta_y = max(0.01, mag * math.sin(angle))

            print (delta_x, delta_y)

            if len(effs_x) == 0:
                effs_x.append(delta_x)
                effs_y.append(delta_y)

            else:
                effs_x.append(effs_x[-1] + delta_x)
                effs_y.append(effs_y[-1] + delta_y)

        return effs_x + effs_y

    def generate_random_cut_combos(self, N_combos, mvas, n_bin):
        if self.verbose:
            print("[GUIDED_OPTIMIZER] Calculating random cut combos for %d bins with mvas" % n_bin, mvas)

        X = []

        for i in range(N_combos):
            if i < 3 and len(mvas) == 1 and n_bin == 1:
                effs_list = list(numpy.random.uniform(0.98,1.0) * numpy.ones(n_bin))
                cuts_list = self.convert_eff_to_cut(mvas[0], effs_list)
            elif len(mvas) == 1:
                effs_list = self.generate_effs(n_bin)
                cuts_list = self.convert_eff_to_cut(mvas[0], effs_list)
            elif len(mvas) == 2:
                effs_list = self.generate_effs_2d(n_bin)
                cuts_list = self.convert_eff_to_cut(mvas[0], effs_list[:n_bin]) + self.convert_eff_to_cut(mvas[1], effs_list[n_bin:]) 
            if self.verbose:
                if i < 10:
                    print("[GUIDED_OPTIMIZER] the %d-th cut combo is " % i, cuts_list, " corresponding to effs of ", effs_list)

            X.append(cuts_list)

        return X

    def generate_random_cut_combos_old(self, N_combos, mvas, n_bin):
        if self.verbose:
            print("[GUIDED_OPTIMIZER] Calculating random cut combos for %d bins with mvas" % n_bin, mvas)
        
        X = []
        for i in range(N_combos):
            cuts_list = []
            effs_list = []
            for mva in mvas:
                reasonable = False
                while not reasonable:
                    effs = self.generate_effs(n_bin)
                    reasonable = self.reasonable_effs(effs)
                if len(effs_list) > 0:
                    effs_list += effs
                else:
                    effs_list = effs

                cuts = self.convert_eff_to_cut(mva, effs)
                if len(cuts_list) > 0:
                    cuts_list += cuts
                else:
                    cuts_list = cuts

            if self.verbose:
                if i < 10:
                    print("[GUIDED_OPTIMIZER] the %d-th cut combo is " % i, cuts_list, " corresponding to effs of ", effs_list)
            X.append(cuts_list)
        return X 

    def convert_eff_to_cut(self, mva, effs):
        cuts = []
        for eff in effs:
            cuts.append(self.convert_single_eff_to_cut(mva, eff))
        return cuts

    def find_nearest(self, array, value):
        val = numpy.ones_like(array)*value
        idx = (numpy.abs(array-val)).argmin()
        return array[idx], idx

    def convert_single_eff_to_cut(self, mva, eff):
        value, idx = self.find_nearest(self.quantiles[mva]["quantiles"], eff)
        return self.quantiles[mva]["scores"][idx][0]

    def subsample(self, X):
        pred = self.predict_limits(X)
        prob = self.calculate_probs(pred)
   
        if self.verbose:
            print("[GUIDED OPTIMIZER] Here are the first few points, along with their predictions and accept probs")
            for i in range(3):
                print("[GUIDED OPTIMIZER] Point: ", X[i], " prediction: %.3f, probability to accept point: %.3f" % (pred[i], prob[i]))

        accept_idx = numpy.nonzero(prob > numpy.random.rand(len(X)))[0]
        while len(accept_idx) == 0:
            print("[GUIDED OPTIMIZER] No accepted points, doubling all probabilities")
            prob *= 2
            accept_idx = numpy.nonzero(prob > numpy.random.rand(len(X)))[0]
        print (accept_idx)

        X = numpy.array(X)

        return list(X[accept_idx])

    def predict_limits(self, X):
        if self.mva == "dnn":
            return self.model.predict([X], batch_size = 10**5)[:,0]
        elif self.mva == "bdt":
            X_frame = pandas.DataFrame(data = X)#, columns = [str(i) for i in range(len(X[0]))])
            return self.bdt.predict(X_frame)

    def calculate_probs(self, pred):
        pred_normalized = pred * (1./self.current_best_lim)

        prob = numpy.exp( -(pred_normalized - 1) / (self.percent_error))

        for i in range(len(prob)):
            if prob[i] > 1.:
                prob[i] = 1.
        return prob

    def calculate_expected_limits(self, points, mvas, n_bin):
        exp_limits = []

        manager = multiprocessing.Manager()
        temp_results = manager.dict() # create this dict that multiprocess childs can talk to

        running_procs = []

        selections = []
        for point in points:
            selections.append(self.get_selection(point, mvas, n_bin))

        # submit jobs
        for i in range(len(selections)):
            if self.verbose:
                print("[GUIDED OPTIMIZER] On selection %d" % i)
                if i < 3:
                    print("[GUIDED OPTIMIZER] Point ", points[i], " was converted to selection string: %s" % selections[i])

            running_procs.append(multiprocessing.Process(target = self.calculate_expected_limit, args = (selections[i], i + (len(selections) * self.iteration_ctr), points[i], temp_results)))
            running_procs[-1].start()

            while True:
                for i in range(len(running_procs)):
                    if not running_procs[i].is_alive():
                        running_procs.pop(i)
                        break
                if len(running_procs) < self.nCores: # if we have less than nCores jobs running, break infinite loop and add another
                    break
                else:
                    os.system("sleep 5s")

        # somewhat hacky (or perhaps elegant?) snippet to wait for last nCores jobs to finish running before we move on
        while len(running_procs) > 0:
            for i in range(len(running_procs)):
                try:
                    if not running_procs[i].is_alive():
                        running_procs.pop(i)
                except:
                    continue

        # extract results from temp_results
        for idx, result in temp_results.items():
            exp_limits.append(result)

        return exp_limits

    def get_selection(self, point, mvas, n_bin):
        assert len(point) == ( len(mvas) * n_bin )

        selection = []
        for i in range(n_bin):
            sel = ""
            for j in range(len(mvas)):
                sel += "%s >= %.6f && " % (mvas[j], point[(j*n_bin) + i])
            sel = sel[:-3] # remove trailing "&& "
            if i > 0:
                sel += " && "
                for k in range(i):
                    sel += "!(%s) && " % selection[k]
            sel = sel[:-3] # remove trailing "&& "
            selection.append(sel)

        return selection

    def process_selection(self, process):
        selection = " ("
        for i in range(len(process_dict[process])):
            selection += "process_id == " + str(process_dict[process][i])
            if i == (len(process_dict[process]) - 1):
                selection += ") "
            else:
                selection += " || "
        print ("selection {}".format(selection))        
        return selection

    #def data_selection(self):
    #    return "(mass > 100 && mass < 180 && 

    def base_selection(self):
        if self.pt_selection == "":
            return "(mass > 100 && mass < 180 && train_label == 2) "
        else:
            return "(mass > 100 && mass < 180 && train_label == 2 && %s) " % self.pt_selection

    def calculate_expected_limit(self, selection, idx, m_point, temp_results):
        yields = {}

        disqualify_srs = False # disqualify certain binning combinations if they don't have enough non-res bkg events in mgg sidebands (require 10 expected)

        for i in range(len(selection)):
            bin = "Bin_%d" % i
            yields[bin] = {}
            for process in self.signal + self.resonant_bkgs:
                signalModelConfig = {
                    "var" : "mass", "weightVar" : "weight_central",
                    "plotpath" : self.scanConfig["plotpath"],
                    "modelpath" : self.scanConfig["modelpath"],
                    "filename" : self.input,
                    "savename" : "CMS-HGG_sigfit_mva_" + process + "_hgg_" + self.channel + "_" + str(i) + "_" + str(idx),
                    "tag" : "hggpdfsmrel_" + process + "_hgg_" + self.channel + "_" + str(i) + "_" + str(idx),
                    "selection" : self.base_selection() + "&&" + self.process_selection(process) + " && " + selection[i],
                }
                if "nottH" in self.resonant_bkgs[0]:
                    simple = True # just fit a single gaussian
                else:
                    simple = False
                model = makeModel(signalModelConfig)
                model.getTree(self.scanner.getTree())
                sig_yield = model.makeSignalModel("wsig_13TeV",
                        { "replaceNorm" : False, "norm_in" : -1, "fixParameters" : True , "simple" : simple},
                )
                yields[bin][process] = sig_yield                

            bkgModelConfig = {
                "var" : "mass", "weightVar" : "weight_central",
                "plotpath" : self.scanConfig["plotpath"],
                "modelpath" : self.scanConfig["modelpath"],
                "filename" : self.input,
                "savename" : "CMS-HGG_bkg_" + self.channel + "_" + str(i) + "_" + str(idx),
                "tag" : "CMS_hgg_bkgshape_" + self.channel + "_" + str(i) + "_" + str(idx),
                "selection" : self.base_selection() + "&&" + self.process_selection(self.nrb_choice) + " && " + selection[i],
            }

            model = makeModel(bkgModelConfig)
            model.getTree(self.scanner.getTree())
            bkg_yield, bkg_yield_full, bkg_yield_raw = model.makeBackgroundModel("wbkg_13TeV", self.channel + "_" + str(i) + "_" + str(idx))

            bkgModelConfig["selection"] = self.base_selection() + "&&" + self.process_selection("data") + " && " + selection[i]
            bkgModelConfig["savename"] = "dummy"
            model2 = makeModel(bkgModelConfig)
            model2.getTree(self.scanner.getTree())
            bkg_yield_data, bkg_yield_data_full, bkg_yield_raw_data = model2.makeBackgroundModel("wdata_13TeV", self.channel + "_" + str(i) + "_" + str(idx) + "dummy")

            #print("[GUIDED OPTIMIZER] Bkg events from fit: %

            yields[bin]["bkg"] = bkg_yield
            if bkg_yield_raw < 5. or bkg_yield_raw_data < 5.:
                print("[GUIDED OPTIMIZER] Only %.6f expected background events in one bin, disqualifying signal region set." % bkg_yield_raw)
                disqualify_srs = True

        datacard = makeCards(self.scanConfig["modelpath"], "CMS-HGG_mva_13TeV_datacard_" + str(idx) + ".txt",
                { "sm_higgs_unc" : self.sm_higgs_unc },
        )
        tagList = [self.channel + "_" + str(x) for x in range(len(selection))]
        sigList = [self.signal[0] + "_hgg"]
        bkgList = ["bkg_mass"]
        for bkg in self.resonant_bkgs:
            bkgList.append(bkg + "_hgg")

        datacard.WriteCard(sigList, bkgList, tagList, "_" + str(idx))
        for tag in tagList:
            datacard = makeCards(self.scanConfig["modelpath"], "CMS-HGG_mva_13TeV_datacard_" + str(idx) + "_" + tag + ".txt",
                                 { "sm_higgs_unc" : self.sm_higgs_unc },
            )
            datacard.WriteCard(sigList, bkgList, [tag], "_" + str(idx))

        combineConfig = {
                "combineOption" : self.combineOption,
                "combineOutName" : "sig_" + str(idx),
                "cardName" : "CMS-HGG_mva_13TeV_datacard_" + str(idx) + ".txt",
                "outtxtName" : "sig_" + str(idx) + ".txt",
        }

        exp_lim, exp_lim_up1sigma, exp_lim_down1sigma, exp_lim_up2sigma, exp_lim_down2sigma = self.scanner.runCombine(combineConfig)
        if "Significance" in self.combineOption:
            exp_lim = 1. / exp_lim # make negative so that we can still minimize the POI
        if disqualify_srs:
            exp_lim *= 3 # triple the expected limit if the SR combination is disqualified bc too few non-res bkg events
            # the reason we triple the exp_lim, is that we still want the expected limit to be a relatively smooth function of the cut values. this way, the optimization bdt can hopefully learn that cut values resulting in very narrow bins have a penalty applied on them

        exp_lim_full = {}
        exp_lim_full["combined"] = [exp_lim, exp_lim_up1sigma, exp_lim_down1sigma, exp_lim_up2sigma, exp_lim_down2sigma]
        
        for tag in tagList:
            combineConfig["combineOutName"] = "sig_" + str(idx) + "_" + tag
            combineConfig["cardName"] = "CMS-HGG_mva_13TeV_datacard_" + str(idx) + "_" + tag + ".txt"
            combineConfig["outtxtName"] = "sig_" + str(idx) + "_" + tag + ".txt"
            lim, lim_up1, lim_down1, lim_up2, lim_down2 = self.scanner.runCombine(combineConfig)
            exp_lim_full[tag] = [lim, lim_up1, lim_down1, lim_up2, lim_down2]

        result = {
           "idx" : idx,
           "x" : [float(x) for x in m_point],
           "exp_lim" : [exp_lim, exp_lim_up1sigma, exp_lim_down1sigma, exp_lim_up2sigma, exp_lim_down2sigma],
           "exp_lim_full" : exp_lim_full,
           "selection" : selection,
           "yields" : yields,
           "disqualified" : str(disqualify_srs)
        }

        temp_results[",".join(selection) + str(idx)] = result

        if self.verbose:
            print("[GUIDED OPTIMIZER]", result)

        return
