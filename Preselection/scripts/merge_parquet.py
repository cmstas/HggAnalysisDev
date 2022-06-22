import awkward
import argparse

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

args = parser.parse_args()
files = [awkward.from_parquet(file) for file in args.input.split(",")]
output = awkward.concatenate(files)

awkward.to_parquet(output,args.output)
