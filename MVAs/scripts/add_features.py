import awkward as ak
import vector
vector.register_awkward()

import argparse
import object_selections as object_selections

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "input parquet file",
    type = str,
    required=True
)

parser.add_argument(
    "--output",
    help = "output parquet file",
    type = str, 
)

parser.add_argument(
    "--variables",
    help = "csv list of variables to be added. Possible choices are \"diphoton\" and \"mjj\" ",
    type = str,
    default="diphoton,mjj" 
)

args = parser.parse_args()
if args.output is None:
    args.output = args.input

df = ak.from_parquet(args.input)

#Diphoton variables
if "diphoton" in args.variables:
    df["Diphoton_pt_mgg"] = df["Diphoton_pt"]/df["Diphoton_mass"]
    df["LeadPhoton_pt_mgg"] = df["LeadPhoton_pt"]/df["Diphoton_mass"]
    df["SubleadPhoton_pt_mgg"] = df["SubleadPhoton_pt"]/df["Diphoton_mass"]
    df["Diphoton_dR"] = object_selections.compute_deltaR(df["LeadPhoton_phi"],df["SubleadPhoton_phi"],
                                                        df["LeadPhoton_eta"],df["SubleadPhoton_eta"])

#Mjj 
# first set mjj then reset it for signal

#make jets
if "mjj" in args.variables:
    jet_pt = ak.concatenate(
        [ak.unflatten(df["jet_%d_pt" % x], 1) for x in range(1,9)],
        axis = 1
    )
    jet_eta = ak.concatenate(
        [ak.unflatten(df["jet_%d_eta" % x], 1) for x in range(1,9)],
        axis = 1
    )
    jet_phi = ak.concatenate(
        [ak.unflatten(df["jet_%d_phi" % x], 1) for x in range(1,9)],
        axis = 1
    )
    jet_mass = ak.concatenate(
        [ak.unflatten(df["jet_%d_mass" % x], 1) for x in range(1,9)],
        axis = 1
    )
    jet_btagDeepFlavB = ak.concatenate(
        [ak.unflatten(df["jet_%d_btagDeepFlavB" % x], 1) for x in range(1,9)],
        axis = 1
    )

    jets = ak.zip({"pt": jet_pt, "eta": jet_eta, "phi": jet_phi, "mass": jet_mass,
                "btagDeepFlavB": jet_btagDeepFlavB})
    p4_jets = ak.Array(jets, with_name='Momentum4D')
    sorted_jets = p4_jets[ak.argsort(p4_jets.btagDeepFlavB,ascending=False)]

    for i in range (1000): #TODO understand jets structure...tmu    
        if p4_jets[i][0].pt != sorted_jets[i][0].pt:
            print ("\np4_jets {} \nsorted_jets {}".format(p4_jets[i],sorted_jets[i])) 
    jj = sorted_jets[:,0] + sorted_jets[:,1]

    df["Dijet_mass"] = jj.mass

    print ("p4_jets {}\nsorted {} \n mjj {}".format(p4_jets,sorted_jets,df["Dijet_mass"]))

# ak.to_parquet(df,args.output)