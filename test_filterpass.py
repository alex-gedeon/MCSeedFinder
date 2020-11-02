import util as ut
import os
from multiprocessing import cpu_count
import shutil

SEARCH_COORDS = "8x0y"
MASTER_FILE = f"seed_bank/quadbank_{SEARCH_COORDS}.txt"
TMP_DIR = "quad_scans/tmp/"

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
    num_splits = cpu_count()
    even_split = len(master_lines) // num_splits
    for idx in range(num_splits):
        if idx == num_splits - 1:
            split = master_lines[idx*even_split:]
        else:
            split = master_lines[idx*even_split:idx*even_split + even_split]
        with open(TMP_DIR + SEARCH_COORDS + "_split" + str(idx) + ".txt", 'w') as outfile:
            outfile.writelines(split)
    
make_splits()

# Set up filter
filter = ["jungle", "shattered_savanna", "ice_spikes"]#, "badlands"]
idict = ut.get_lookup_table()
enum_ints = sorted([idict[key] for key in filter])
enum_ints = [str(val) for val in enum_ints]

os.system(f'./find_filtered_biomes {cpu_count()} 1024 extra/10k_8x0y.txt {" ".join(enum_ints)}')
