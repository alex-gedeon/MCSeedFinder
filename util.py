import subprocess
import os
from PIL import Image, ImageDraw
import multiprocessing as mp
import time
import glob
import shutil


def scan_quadseeds(qx, qy, search_time, quadfile):
    process = subprocess.Popen(
        ['./find_quadhuts', str(qx), str(qy)], stdout=open(quadfile, 'w'))
    try:
        print(
            f'Generating quad witch hut seeds at ({qx * 512}, {qy * 512}) for {search_time} seconds...')
        process.wait(timeout=search_time)
    except subprocess.TimeoutExpired:
        process.kill()

    # Remove last line from file
    with open(quadfile) as qf:
        lines = qf.readlines()[:-1]
        qf.close()

    with open(quadfile, 'w') as qf:
        qf.writelines(lines)
        qf.close()
    print(f'Found {len(lines)} quad witch hut seeds!')


def convert_all_ppm_to_png(seedlist, folder, xsize=1024, ysize=512):
    """Create png image given seed and folder."""

    # Create folder, make sure it exists
    folder = folder.strip().rstrip('/') + "/"
    if not os.path.exists(os.path.dirname(folder)):
        os.makedirs(os.path.dirname(folder))

    def convert_single_ppm(seed):
        ppm_filepath = folder + str(seed)
        # Call c binary to generate ppm
        os.system(f'./image_generator {seed} {folder}/ {xsize} {ysize}')
        while not os.path.exists(ppm_filepath + '.ppm'):
            time.sleep(0.1)

        # Convert ppm to png, remove ppm to save space
        im = Image.open(f'{ppm_filepath}.ppm')
        draw = ImageDraw.Draw(im)
        draw.rectangle([im.width//2 - 20, im.height//2 - 20, im.width //
                        2 + 20, im.height//2 + 20], width=4, outline="#ff0000")
        im.save(f'{ppm_filepath}.png')
        os.remove(f'{ppm_filepath}.ppm')

    def convert_batch_ppm(miniseedlist):
        for seed in miniseedlist:
            seed = int(seed.strip())
            convert_single_ppm(seed)

    # Determine number of processes and splits per process
    num_processes = mp.cpu_count()
    even_split = len(seedlist) // num_processes

    processpool = []

    # Create a process for each split, split into even chunks
    for idx in range(num_processes):
        # If last index, give rest
        if idx == num_processes - 1:
            a = mp.Process(target=convert_batch_ppm, args=[
                           seedlist[idx*even_split:]])
        else:
            a = mp.Process(target=convert_batch_ppm, args=[
                           seedlist[idx*even_split:idx*even_split + even_split]])

        a.start()
        processpool.append(a)

    # Attempt to join processes
    for process in processpool:
        process.join()


def get_lookup_table():
    return {
        "ocean": 0,
        "deep_ocean": 24,
        "frozen_ocean": 10,
        "deep_frozen_ocean": 50,
        "cold_ocean": 46,
        "deep_cold_ocean": 49,
        "lukewarm_ocean": 45,
        "deep_lukewarm_ocean": 48,
        "warm_ocean": 44,
        "deep_warm_ocean": 47,
        "river": 7,
        "frozen_river": 11,
        "beach": 16,
        "stone_shore": 25,
        "snowy_beach": 26,
        "forest": 4,
        "wooded_hills": 18,
        "flower_forest": 132,
        "birch_forest": 27,
        "birch_forest_hills": 28,
        "tall_birch_forest": 155,
        "tall_birch_hills": 156,
        "dark_forest": 29,
        "dark_forest_hills": 157,
        "jungle": 21,
        "jungle_hills": 22,
        "modified_jungle": 149,
        "jungle_edge": 23,
        "modified_jungle_edge": 151,
        "bamboo_jungle": 168,
        "bamboo_jungle_hills": 169,
        "taiga": 5,
        "taiga_hills": 19,
        "taiga_mountains": 133,
        "snowy_taiga": 30,
        "snowy_taiga_hills": 31,
        "snowy_taiga_mountains": 158,
        "giant_tree_taiga": 32,
        "giant_tree_taiga_hills": 33,
        "giant_spruce_taiga": 160,
        "giant_spruce_taiga_hills": 161,
        "mushroom_fields": 14,
        "mushroom_field_shore": 15,
        "swamp": 6,
        "swamp_hills": 134,
        "savanna": 35,
        "savanna_plateau": 36,
        "shattered_savanna": 163,
        "shattered_savanna_plateau": 164,
        "plains": 1,
        "sunflower_plains": 129,
        "desert": 2,
        "desert_hills": 17,
        "desert_lakes": 130,
        "snowy_tundra": 12,
        "snowy_mountains": 13,
        "ice_spikes": 140,
        "mountains": 3,
        "wooded_mountains": 34,
        "gravelly_mountains": 131,
        "modified_gravelly_mountains": 162,
        "mountain_edge": 20,
        "badlands": 37,
        "badlands_plateau": 39,
        "modified_badlands_plateau": 167,
        "wooded_badlands_plateau": 38,
        "modified_wooded_badlands_plateau": 166,
        "eroded_badlands": 165,
        "nether_wastes": 8,
        "crimson_forest": 171,
        "warped_forest": 172,
        "soul_sand_valley": 170,
        "basalt_deltas": 173,
        "the_end": 9,
        "small_end_islands": 40,
        "end_midlands": 41,
        "end_highlands": 42,
        "end_barrens": 43,
        "the_void": 127,
    }


def get_filter(given_filter=None, filter_path='biome_filters.txt'):
    """Read in user-defined filter from file."""
    if not os.path.exists(filter_path):
        open(filter_path, 'w').close()
    fil_lines = open(filter_path).readlines()
    if len(fil_lines) == 0:
        print("Error: no filters found in", filter_path)
        exit(1)

    # Only query user if option is not used
    if given_filter is None:
        print("Select a filter out of the following:")
        for idx, line in enumerate(fil_lines):
            print(f"    {idx}: {line.strip()}")
        filter_selection = int(input())
    else:
        filter_selection = given_filter
    user_filter = fil_lines[filter_selection]
    user_filter = [val.strip() for val in user_filter.split(', ')]
    return user_filter, filter_selection


def get_search_coords(bank_folder="seed_bank/"):
    """
    Get all coords from seed bank files.

    Example filename: "seed_bank/quadbank_8x0y.txt"
    """
    s_coords = [fil.split("/")[1].split("_")[1].split(".")[0]
                for fil in glob.glob(bank_folder + "*.txt")]
    if len(s_coords) == 0:
        print(
            f"Error: no seed files found in '{bank_folder}', generate some with ./find_quadhuts")
        exit(1)
    return s_coords


def make_splits(master_file, search_coords, tmp_dir="quad_scans/tmp/"):
    """Generate equal splits of master seedfile in tmp_dir."""
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
        os.mkdir(tmp_dir)

    # Read in master file
    master_lines = open(master_file).readlines()

    # Split master file to separate files
    num_splits = mp.cpu_count()
    even_split = len(master_lines) // num_splits
    for idx in range(num_splits):
        if idx == num_splits - 1:
            split = master_lines[idx*even_split:]
        else:
            split = master_lines[idx*even_split:idx *
                                 even_split + even_split]
        with open(tmp_dir + search_coords + "_split" + str(idx) + ".txt", 'w') as outfile:
            outfile.writelines(split)


def ensure_scan_structure(filter_id, search_range, scan_folder="quad_scans/", tmp_dir="tmp/"):
    """Ensures base folder structure exists."""
    if not os.path.exists(scan_folder):
        os.mkdir(scan_folder)
    if not os.path.exists(scan_folder + tmp_dir):
        os.mkdir(scan_folder + tmp_dir)
    filter_path = scan_folder + f"filter{filter_id}_{search_range}r/"
    if not os.path.exists(filter_path):
        os.mkdir(filter_path)
    if os.path.exists(filter_path + "all/"):
        shutil.rmtree(filter_path + "all/")
    os.mkdir(filter_path + "all/")


def run_biome_scan(biome_ids, search_coords, search_range, tmp_dir="quad_scans/tmp/"):
    """
    Scans splits of seedbank file in C.

    Writes to filtered files per split in tmp_dir, waits until complete.
    """
    args = [
        './find_filtered_biomes',
        str(mp.cpu_count()),
        str(search_range),
        tmp_dir + search_coords + ".txt"
    ]
    args += biome_ids

    filter_process = subprocess.Popen(args)
    filter_process.wait()


def aggregate_scan(filter_id, search_coords, search_range, scan_folder="quad_scans/", tmp_dir="quad_scans/tmp/"):
    base_dir = f"{scan_folder}filter{filter_id}_{search_range}r/"
    export_folder = base_dir + search_coords + "/"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if not os.path.exists(export_folder):
        os.mkdir(export_folder)

    EXPORT_PATH = export_folder + search_coords + "_filtered.txt"
    export_file = open(EXPORT_PATH, "w")

    for idx in range(mp.cpu_count()):
        fil_path = tmp_dir + search_coords + \
            "_split" + str(idx) + "_filtered.txt"
        filtered_lines = open(fil_path).readlines()
        export_file.writelines(filtered_lines)
    export_file.close()

    return EXPORT_PATH


def generate_images(export_filepath):
    generated_path = os.path.dirname(export_filepath) + "/generated/"
    filtered_lines = open(export_filepath).readlines()
    if os.path.exists(generated_path):
        shutil.rmtree(generated_path)
    convert_all_ppm_to_png(filtered_lines, generated_path)

    all_path = os.path.dirname(os.path.dirname(export_filepath)) + "/all/"
    os.system(f'cp {generated_path}* {all_path} 2>/dev/null')
