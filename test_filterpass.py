import util as ut
import os
import multiprocessing as mp
import shutil
import subprocess

SEARCH_COORDS = "8x0y"
# MASTER_FILE = f"extra/100k_{SEARCH_COORDS}.txt"
MASTER_FILE = f"seed_bank/quadbank_{SEARCH_COORDS}.txt"
TMP_DIR = "quad_scans/tmp/"
BASE_DIR = "quad_scans/"
SEARCH_RANGE = 1024

def make_splits():
    if not os.path.exists(TMP_DIR):
        os.mkdir("quad_scans/tmp/")
    else:
        shutil.rmtree("quad_scans/tmp/")
        os.mkdir("quad_scans/tmp/")

    # Read in master file
    master_lines = open(MASTER_FILE).readlines()
    # master_lines.sort()

    # Split master file to separate files
    num_splits = mp.cpu_count()
    even_split = len(master_lines) // num_splits
    for idx in range(num_splits):
        if idx == num_splits - 1:
            split = master_lines[idx*even_split:]
        else:
            split = master_lines[idx*even_split:idx*even_split + even_split]
        with open(TMP_DIR + SEARCH_COORDS + "_split" + str(idx) + ".txt", 'w') as outfile:
            outfile.writelines(split)
    
# make_splits()

# Set up filter
filter = ["jungle", "shattered_savanna", "ice_spikes", "badlands", "frozen_ocean"]
idict = ut.get_lookup_table()
enum_ints = sorted([idict[key] for key in filter])  # todo: make sure if sorting is needed
enum_ints = [str(val) for val in enum_ints]

# os.system(f'./find_filtered_biomes {mp.cpu_count()} 1024 {TMP_DIR + SEARCH_COORDS + ".txt"} {" ".join(enum_ints)}')

args = [
        './find_filtered_biomes',
        str(mp.cpu_count()),
        str(SEARCH_RANGE),
        TMP_DIR + SEARCH_COORDS + ".txt"
]
for enum_int in enum_ints:
    args.append(enum_int)

# filter_process = subprocess.Popen(args)
# filter_process.wait()

import util as ut

# read in and concat

export_file = open(BASE_DIR + SEARCH_COORDS + "_filtered.txt", "w")

for idx in range(mp.cpu_count()):
    fil_path = TMP_DIR + SEARCH_COORDS + "_split" + str(idx) + "_filtered.txt"
    filtered_lines = open(fil_path).readlines()
    export_file.writelines(filtered_lines)
    # os.remove(fil_path)
export_file.close()
