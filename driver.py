import util as ut
import os
import multiprocessing as mp
import shutil
import subprocess
import click


@click.command()
@click.option('--search_range', type=int, default=1024)
@click.option('--biome_filter', type=int, default=None)
def main(search_range, biome_filter):
    user_filter = ut.get_filter(given_filter=biome_filter)
    print(f"Scanning with {', '.join(user_filter[:])}")

    search_coords = ut.get_search_coords()
    print(search_coords)

    ut.ensure_scan_structure()
    for s_idx, s_coord in enumerate(search_coords):
        print(
            f"Starting search in {s_coord}, no. {s_idx + 1}/{len(search_coords)} total")
        master_filepath = f"seed_bank/quadbank_{s_coord}.txt"
        ut.make_splits(master_filepath, s_coord)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter

exit()

SEARCH_COORDS = "8x0y"
TMP_DIR = "quad_scans/tmp/"
BASE_DIR = f"quad_scans/filter_{filter_selection}/"
SEARCH_RANGE = 1024


for s_idx, SEARCH_COORDS in enumerate(s_coords):
    print(f"Starting search in {SEARCH_COORDS}, {s_idx}/{len(s_coords)} done")
    # MASTER_FILE = f"extra/100k_{SEARCH_COORDS}.txt"
    MASTER_FILE = f"seed_bank/quadbank_{SEARCH_COORDS}.txt"
    EXPORT_FOLDER = BASE_DIR + SEARCH_COORDS + "/"

    idict = ut.get_lookup_table()
    enum_ints = [str(idict[key]) for key in user_filter]

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

    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    if not os.path.exists(EXPORT_FOLDER):
        os.mkdir(EXPORT_FOLDER)

    EXPORT_PATH = EXPORT_FOLDER + SEARCH_COORDS + "_filtered.txt"
    export_file = open(EXPORT_PATH, "w")

    for idx in range(mp.cpu_count()):
        fil_path = TMP_DIR + SEARCH_COORDS + \
            "_split" + str(idx) + "_filtered.txt"
        filtered_lines = open(fil_path).readlines()
        export_file.writelines(filtered_lines)
    export_file.close()

    # print(EXPORT_PATH)
    filtered_lines = open(EXPORT_PATH).readlines()
    photo_path = EXPORT_FOLDER + "generated/"
    if os.path.exists(photo_path):
        shutil.rmtree(photo_path)
    ut.convert_all_ppm_to_png(filtered_lines, photo_path)

ALL_PATH = BASE_DIR + "all"

if os.path.exists(ALL_PATH):
    shutil.rmtree(ALL_PATH)
    os.mkdir(ALL_PATH)
else:
    os.mkdir(ALL_PATH)
os.system(f'cp {BASE_DIR}/*/generated/* {ALL_PATH}')

print("\nResults:")
os.system(
    f'echo "Found" $(find {BASE_DIR}*/generated/* | wc -l) "matches out of" $(cat seed_bank/* | wc -l) "total"')
