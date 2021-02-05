import numpy
import random
from sklearn import metrics

def calc_auc(y, pred, sample_weight, interp = 10000):
    """
    Make interpolated roc curve and calculate AUC.

    Keyword arguments:
    y -- array of labels
    pred -- array of mva scores
    sample_weight -- array of per-event weights
    interp -- number of points in resulting fpr and tpr arrays
    """

    fpr, tpr, thresh = metrics.roc_curve(
        y,
        pred,
        pos_label = 1,
        sample_weight = sample_weight
    )

    fpr = sorted(fpr)
    tpr = sorted(tpr)

    fpr_interp = numpy.linspace(0, 1, interp)
    tpr_interp = numpy.interp(fpr_interp, fpr, tpr) # recalculate tprs at each fpr

    auc = metrics.auc(fpr, tpr)

    results = {
        "fpr" : fpr_interp,
        "tpr" : tpr_interp,
        "auc" : auc
    }
    return results

def bootstrap_indices(x):
    """
    Return array of indices of len(x) to make bootstrap resamples 
    """

    return numpy.random.randint(0, len(x), len(x))
    

def calc_roc_and_unc(y, pred, sample_weight, n_bootstrap = 10, interp = 10000):
    """
    Calculates tpr and fpr arrays (with uncertainty for tpr) and auc and uncertainty

    Keyword arguments:
    y -- array of labels
    pred -- array of mva scores
    sample_weight -- array of per-event weights
    n_bootstrap -- number of bootstrap resamples to use for calculating uncs
    interp -- number of points in resulting fpr and tpr arrays
    """

    y = numpy.array(y)
    pred = numpy.array(pred)
    sample_weight = numpy.array(sample_weight)

    results = calc_auc(y, pred, sample_weight)
    fpr, tpr, auc = results["fpr"], results["tpr"], results["auc"]
    
    fprs = [fpr] 
    tprs = [tpr]
    aucs = [auc]

    for i in range(n_bootstrap):
        idx = bootstrap_indices(y)
        
        label_bootstrap   = y[idx]
        pred_bootstrap    = pred[idx]
        weights_bootstrap = sample_weight[idx]

        results_bootstrap = calc_auc(label_bootstrap, pred_bootstrap, weights_bootstrap, interp)
        fpr_b, tpr_b, auc_b = results_bootstrap["fpr"], results_bootstrap["tpr"], results_bootstrap["auc"]
        fprs.append(fpr_b)
        tprs.append(tpr_b)
        aucs.append(auc_b)

    unc = numpy.std(auc)
    tpr_mean = numpy.mean(tprs, axis=0)
    tpr_unc = numpy.std(tprs, axis=0)
    fpr_mean = numpy.mean(fprs, axis=0)

    results = {
        "auc" : auc,
        "auc_unc" : unc,
        "fpr" : fpr_mean,
        "tpr" : tpr_mean,
        "tpr_unc" : tpr_unc
    }

    return results

def make_train_test_validation_split(df):
    mgg = df["ggMass"].tolist()
    digits = numpy.array([int(str(m).split(".")[1]) for m in mgg])

    idx_train = numpy.argwhere(digits % 3 == 0).ravel() # ravel() to make it the right shape for slicing df
    idx_test = numpy.argwhere(digits % 3 == 1).ravel()
    idx_validation = numpy.argwhere(digits % 3 == 2).ravel()

    # Record the test/train/validation split
    # Train = 0, Test = 1, Validation = 2
    train_label = list(numpy.ones(len(df)) * -1)
    df["train_label"] = train_label

    df.iloc[idx_train, df.columns.get_loc("train_label")] = 0
    df.iloc[idx_test, df.columns.get_loc("train_label")] = 1
    df.iloc[idx_validation, df.columns.get_loc("train_label")] = 2

    return df, idx_train, idx_test, idx_validation
