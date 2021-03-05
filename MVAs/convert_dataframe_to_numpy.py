import pandas
import numpy

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input", help = "input df", type=str, default = "output/test_finalfit_df.pkl")
args = parser.parse_args()

"""
Script to convert pandas dataframe to numpy array.
Next (in another script) we can convert the numpy array to a TTree
so that it can be used with the ttH/FCNC binning scripts.
"""

def to_tensor(dataframe, columns = [], dtypes = {}):
    # Use all columns from data frame if none where listed when called
    if len(columns) <= 0:
        columns = dataframe.columns
    # Build list of dtypes to use, updating from any `dtypes` passed when called
    dtype_list = []
    for column in columns:
        if column not in dtypes.keys():
            dtype_list.append(dataframe[column].dtype)
        else:
            dtype_list.append(dtypes[column])
    # Build dictionary with lists of column names and formatting in the same order
    dtype_dict = {
        'names': columns,
        'formats': dtype_list
    }
    # Initialize _mostly_ empty nupy array with column names and formatting
    numpy_buffer = numpy.zeros(
        shape = len(dataframe),
        dtype = dtype_dict)
    # Insert values from dataframe columns into numpy labels
    for column in columns:
        numpy_buffer[column] = dataframe[column].to_numpy()
    # Return results of conversion
    return numpy_buffer

events = pandas.read_pickle(args.input)
events = events.rename(columns = { "gg_mass" : "mass" } )
events["weight"] = events["weight"] * 3
events = to_tensor(events)

output = "output/" + args.input.split("/")[-1].replace(".pkl", ".npz")
numpy.savez(output, events = events)
