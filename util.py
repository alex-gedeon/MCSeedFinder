import subprocess
import os
from PIL import Image, ImageDraw
import multiprocessing as mp
import time


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


def filter_quadseeds(quadfile, outfile):
    # Open and sort quadfile
    quads = open(quadfile).readlines()
    quads.sort()

    # Internal function to search for seeds
    def search_seeds(seedlist):
        for line in seedlist:
            line = int(line.strip())
            os.system(
                f'./find_filtered_biomes {int(line)} {int(line) + 1} >> {outfile}')

    def search_seeds_reporter(seedlist):
        last_perc = -1
        for idx, line in enumerate(seedlist):
            # If at percentage point, print out
            if round(idx/len(seedlist) * 100) != last_perc:
                print(f"\rProgress: {round(idx/len(seedlist) * 100)}%", end="")
                last_perc = round(idx/len(seedlist) * 100)
            line = int(line.strip())
            os.system(
                f'./find_filtered_biomes {int(line)} {int(line) + 1} >> {outfile}')
        print("\rProgress: 100%   ")

    # Determine number of processes and splits per process
    num_processes = mp.cpu_count()
    even_split = len(quads) // num_processes

    processpool = []
    # Create a process for each split, split into even chunks
    for idx in range(num_processes):
        # If last index, give rest
        if idx == num_processes - 1:
            a = mp.Process(target=search_seeds_reporter,
                           args=[quads[idx*even_split:]])
        else:
            a = mp.Process(target=search_seeds, args=[
                           quads[idx*even_split:idx*even_split + even_split]])
        a.start()
        processpool.append(a)

    # Attempt to join processes
    for process in processpool:
        process.join()

    num_found = len(open(outfile).readlines())

    print(f"Searched {len(quads)} seeds, found {num_found} matches!")


def convert_all_ppm_to_png(seedlist, folder, xsize=512, ysize=256):
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
