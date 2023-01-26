import numpy
import awkward as ak

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input", help = "input df", type=str, default = "output/test_finalfit_df.parquet")
args = parser.parse_args()

"""
Script to convert awkward array dataframe to numpy array.
Next (in another script) we can convert the numpy array to a TTree
so that it can be used with the ttH/FCNC binning scripts.
"""

def to_tensor(dataframe, columns = [], dtypes = {}):
    # Use all columns from data frame if none where listed when called
    if len(columns) <= 0:
        columns = dataframe.fields
    # Build list of dtypes to use, updating from any `dtypes` passed when called
    dtype_list = []
    for column in columns:
        if column not in dtypes.keys():
            dtype_list.append(type(dataframe[column][0]))
        else:
            dtype_list.append(dtypes[column])
    # Build dictionary with lists of column names and formatting in the same order
    dtype_dict = {
        'names': columns,
        'formats': dtype_list
    }
    # Initialize _mostly_ empty numpy array with column names and formatting
    numpy_buffer = numpy.zeros(
        shape = len(dataframe),
        dtype = dtype_dict)
    # Insert values from dataframe columns into numpy labels
    for column in columns:
        print("column {}\n buffer {}\n dataframe{}".format(column, numpy_buffer[column].shape , dataframe[column].to_numpy().shape) )
        numpy_buffer[column] = dataframe[column].to_numpy()
    # Return results of conversion
    return numpy_buffer

if "parquet" in args.input:
    events = ak.from_parquet(args.input)
else : events = ak.from_pickle(args.input)
events['mass'] = events.Diphoton_mass

f = events.fields.remove('Diphoton_mass')
events["weight_central"] = events["weight_central"] * 3
events = to_tensor(events)

output = "output/" + args.input.split("/")[-1].replace(".parquet", ".npz")
# output = "output/" + args.input.split("/")[-1].replace(".pkl", ".npz")
numpy.savez(output, events = events)
