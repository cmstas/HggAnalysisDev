import argparse
import awkward
import json
import os

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Merge new processes in existing df")
        
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        help = "input dir containig parquet file",
        type = str,
        required=True
    )

    parser.add_argument(
        "--target",
        help = "target parquet file",
        type = str, 
    )


    parser.add_argument(
        "--combine_dir",
        help = "output dir",
        type = str, 
    )


    parser.add_argument(
        "--processes",
        help = "csv list of processes from input df to be added into the output one",
        type = str,
)

    return parser.parse_args()

args = parse_arguments()

def combine_dataframes(args):
    with open(args.input + '/summary.json') as f_in:
        new_summary = json.load(f_in)
    with open(args.target + '/summary.json') as f_in:
        old_summary = json.load(f_in)
    print(old_summary['sample_id_map'])
    print(new_summary['sample_id_map'])


    new_df = awkward.from_parquet(args.input + '/merged_nominal.parquet')
    old_df = awkward.from_parquet(args.target + '/merged_nominal.parquet')
    n_old_procs = len(old_summary['sample_id_map'])
   
    proc =args.processes
    if proc not in new_summary['sample_id_map']:
        print("process {} not found".format(proc))
        quit()
    new_summary['sample_id_map'][proc] += n_old_procs
    print(new_summary['sample_id_map'])

    new_df['process_id'] = new_df.process_id + n_old_procs
    combined_df = awkward.concatenate([new_df,old_df])

    os.mkdir(args.combine_dir)
    awkward.to_parquet(combined_df, args.combine_dir + '/merged_nominal.parquet')        

combine_dataframes(args)