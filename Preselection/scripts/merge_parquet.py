import awkward
import argparse
import pickle

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "comma separated list of parquet files",
    type = str,
)
parser.add_argument(
    "--output",
    help = "output parquet",
    type = str,
    default = "../output/merged_output.parquet"
)

def write_to_df(self, events, output_name):
        df = awkward.to_pandas(events)
        df.to_pickle(output_name)
        return

args = parser.parse_args()



files = [awkward.from_parquet(file) for file in args.input.split(",")]
print ("\nMerging {} files:".format(len(files)))
for file in files:
    print (file)
output = awkward.concatenate(files)
write_to_df(output,args.output.replace(".parquet",".pkl"))
awkward.to_parquet(output,args.output)

