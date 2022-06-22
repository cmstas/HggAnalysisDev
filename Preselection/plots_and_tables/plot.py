import json
import argparse
import pandas
import plotter

parser = argparse.ArgumentParser()
parser.add_argument(
    "--events",
    help = "path to dataframe with events to plot",
    type = str,
)
parser.add_argument(
    "--plot_options",
    help = "path to json with plot options",
    type = str
)
parser.add_argument(
    "--events_options",
    help = "path to json with info about events (will be assumed to be the same path as --events if nothing is specified",
    type = str,
    default = None
)
parser.add_argument(
    "--debug",
    help = "debug",
    action = "store_true"
)
args = parser.parse_args()

events_json = args.events.replace(".pkl", ".json") if args.events_options is None else args.events_options

if ".parquet" in args.events:
    input_df = pandas.read_parquet(args.events)
else:
    input_df = args.events

plot_helper = plotter.Plotter(
    df = input_df,
    plot_options = args.plot_options,
    input_options = events_json,
    debug = args.debug,
    branches = "all"
)
plot_helper.run()
