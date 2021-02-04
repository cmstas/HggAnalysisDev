import pandas
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--samples",
    help = "path to json file containing samples & metadata",
    type = str,
    default = "../data/samples_and_scale1fb.json"
)
parser.add_argument(
    "--events",
    help = "path to pkl file containing events",
    type = str
)

args = parser.parse_args()

with open(args.samples, "r") as f_in:
    samples = json.load(f_in)

events = pandas.read_pickle(args.events)

def make_std_yield_table(samples, events, cuts = None):
    results = {}
    for sample, info in samples.items():
        process_id = info["process_id"]
        events_process = events[events["process_id"] == process_id]
        n_events_raw = len(events_process)
        n_events_weighted = events_process["weight"].sum()
        results[sample] = n_events_weighted
    return results

results_incl = make_std_yield_table(samples, events)

events_1lep_0tau = events[(events["n_electrons"] + events["n_muons"] == 1) & (events["n_tau"] == 0)]
events_0lep_1tau = events[(events["n_electrons"] == 0) & (events["n_muons"] == 0) & (events["n_tau"] == 1)]
events_1lep_1tau = events[(events["n_electrons"] + events["n_muons"] == 1) & (events["n_tau"] == 1)]
events_0lep_2tau = events[(events["n_electrons"] + events["n_muons"] == 0) & (events["n_tau"] >= 2)]
events_2lep_0tau = events[(events["n_electrons"] + events["n_muons"] >= 2) & (events["n_tau"] == 0)]

results_1lep_0tau = make_std_yield_table(samples, events_1lep_0tau)
results_0lep_1tau = make_std_yield_table(samples, events_0lep_1tau)
results_1lep_1tau = make_std_yield_table(samples, events_1lep_1tau)
results_0lep_2tau = make_std_yield_table(samples, events_0lep_2tau)
results_2lep_0tau = make_std_yield_table(samples, events_2lep_0tau)

results = {
    "inclusive" : results_incl,
    "1lep_0tau" : results_1lep_0tau,
    "0lep_1tau" : results_0lep_1tau,
    "1lep_1tau" : results_1lep_1tau,
    "0lep_2tau" : results_0lep_2tau,
    "2lep_0tau" : results_2lep_0tau
}

with open("yields.json", "w") as f_out:
    json.dump(results, f_out, sort_keys = True, indent = 4)
