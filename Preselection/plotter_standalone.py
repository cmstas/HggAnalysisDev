import argparse

from plots_and_tables import plotter

"""
Wrapper for the One Plotter(TM)
"""

parser = argparse.ArgumentParser()

parser.add_argument("--input", "-i", help="Input dataframe", type=str)

parser.add_argument(
    "--config", "-c", help="Plot config json location", type=str
)

parser.add_argument("--debug", "-d", help="Debug flag", action="store_true")


args = parser.parse_args()
p = plotter.Plotter(
    df=args.input, plot_options=args.config, branches="all", debug=args.debug
)
p.run()
