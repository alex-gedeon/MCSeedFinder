import util as ut
import os
import multiprocessing as mp
import shutil
import subprocess

SEARCH_COORDS = "8x0y"
TMP_DIR = "quad_scans/tmp/"
BASE_DIR = "quad_scans/"

s_coords = []
for root, dirs, files in os.walk("seed_bank/"):
    for fil in files:
        fil = fil.split("_")[1].split(".")[0]
        s_coords.append(fil)

for s_idx, SEARCH_COORDS in enumerate(s_coords):
    print(f"Starting search in {SEARCH_COORDS}, {s_idx}/{len(s_coords)} done")
    # MASTER_FILE = f"extra/100k_{SEARCH_COORDS}.txt"
    MASTER_FILE = f"seed_bank/quadbank_{SEARCH_COORDS}.txt"
    EXPORT_FOLDER = BASE_DIR + SEARCH_COORDS + "/"
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
        
    make_splits()

    # Set up filter
    filter = ["jungle", "shattered_savanna", "ice_spikes", "badlands", "frozen_ocean", "warm_ocean"]
    # filter = ["giant_tree_taiga_hills", "jungle", "shattered_savanna", "ice_spikes", "badlands", "frozen_ocean", "warm_ocean"]
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

    # Run search
    filter_process = subprocess.Popen(args)
    filter_process.wait()

    import util as ut

    # read in and concat

    if not os.path.exists(EXPORT_FOLDER):
        os.mkdir(EXPORT_FOLDER)

    EXPORT_PATH = EXPORT_FOLDER + SEARCH_COORDS + "_filtered.txt"
    export_file = open(EXPORT_PATH, "w")

    for idx in range(mp.cpu_count()):
        fil_path = TMP_DIR + SEARCH_COORDS + "_split" + str(idx) + "_filtered.txt"
        filtered_lines = open(fil_path).readlines()
        export_file.writelines(filtered_lines)
    export_file.close()

    # print(EXPORT_PATH)
    filtered_lines = open(EXPORT_PATH).readlines()
    photo_path = EXPORT_FOLDER + "generated/"
    if os.path.exists(photo_path):
        shutil.rmtree(photo_path)
    ut.convert_all_ppm_to_png(filtered_lines, photo_path)

if os.path.exists('quad_scans/all/'):
    shutil.rmtree('quad_scans/all/')
else:
    os.mkdir('quad_scans/all/')
os.system('cp quad_scans/*/generated/* quad_scans/all')

print("\nResults:")
os.system('echo "Found" $(find quad_scans/*/generated/* | wc -l) "matches out of" $(cat seed_bank/* | wc -l) "total"')
