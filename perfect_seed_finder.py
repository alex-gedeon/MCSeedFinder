import os, sys, click, subprocess, time
import multiprocessing as mp
from PIL import Image, ImageDraw
from shutil import rmtree
import datetime as dt


def scan_quadseeds(qx, qy, search_time, quadfile):
    process = subprocess.Popen(['./find_quadhuts', str(qx), str(qy)], stdout=open(quadfile, 'w'))
    try:
        print(f'Generating quad witch hut seeds at ({qx * 512}, {qy * 512}) for {search_time} seconds...')
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
            os.system(f'./find_compactbiomes {int(line)} {int(line) + 1} >> {outfile}')
    
    def search_seeds_reporter(seedlist):
        last_perc = -1
        for idx, line in enumerate(seedlist):
            # If at percentage point, print out
            if round(idx/len(seedlist) * 100) != last_perc:
                print(f"\rProgress: {round(idx/len(seedlist) * 100)}%", end="")
                last_perc = round(idx/len(seedlist) * 100)
            line = int(line.strip())
            os.system(f'./find_compactbiomes {int(line)} {int(line) + 1} >> {outfile}')
        print("\rProgress: 100%   ")

    # Determine number of processes and splits per process
    num_processes = mp.cpu_count()
    even_split = len(quads) // num_processes

    processpool = []
    # Create a process for each split, split into even chunks
    for idx in range(num_processes):
        # If last index, give rest
        if idx == num_processes - 1:
            a = mp.Process(target=search_seeds_reporter, args=[quads[idx*even_split:]])
        else:
            a = mp.Process(target=search_seeds, args=[quads[idx*even_split:idx*even_split + even_split]])
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
        draw.rectangle([im.width//2 - 20, im.height//2 - 20, im.width//2 + 20, im.height//2 + 20], width=4, outline="#ff0000")
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
            a = mp.Process(target=convert_batch_ppm, args=[seedlist[idx*even_split:]])
        else:
            a = mp.Process(target=convert_batch_ppm, args=[seedlist[idx*even_split:idx*even_split + even_split]])
            
        a.start()
        processpool.append(a)

    # Attempt to join processes
    for process in processpool:
        process.join()

@click.command()
@click.argument('qx', type=int, required=True)
@click.argument('qy', type=int, required=True)
@click.argument('search_time', type=int, default=5)
@click.option('--force', type=bool, default=False)
def main(qx, qy, search_time, force):

    ########### Step 1: Generate Seeds ###########

    # Create folder to store quad scan files
    if not os.path.exists('quad_scans/'):
        os.mkdir('quad_scans/')
    
    # Check if quadfile already exists
    quadfile = f'quad_scans/quadseeds_{qx}x{qy}y.txt'
    run_scan = True
    if not os.path.exists(quadfile):
        open(quadfile, 'x').close()
    elif not force:
        rerun = input("Quadfile already exists, rerun anyways? (y/n): ")
        while rerun not in ['y', 'n']:
            rerun = input("Quadfile already exists, rerun anyways? (y/n): ")
        run_scan = True if rerun == 'y' else False

    # Run the scan on the quadfile if necessary
    if run_scan:
        scan_quadseeds(qx, qy, search_time, quadfile)
        
    ########### Step 2: Filter Seeds ###########
    
    filtered_file = quadfile[:-4] + "_filtered.txt"  # remove .txt and add suffix

    # Remove existing filtered file if exists
    run_scan = True
    if os.path.exists(filtered_file) and not force:
        rerun = input("Filter quadfile already exists, rerun anyways? (y/n): ")
        while rerun not in ['y', 'n']:
            rerun = input("Filter quadfile already exists, rerun anyways? (y/n): ")
        run_scan = True if rerun == 'y' else False
    if run_scan:
        if os.path.exists(filtered_file):
            os.remove(filtered_file)
        print("\nFiltering seeds as per generator.h...")
        currt = dt.datetime.now()
        filter_quadseeds(quadfile, filtered_file)
        print(f"  ~{round((dt.datetime.now() - currt).total_seconds(), 4)} seconds")

    ########### Step 3: Create Images ###########

    # Create image path if exists, else delete
    img_path = f'quad_scans/quadseeds_{qx}x{qy}y_images/'
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    else:
        rmtree(img_path)

    
    with open(filtered_file) as flfile:
        lines = flfile.readlines()
        currt = dt.datetime.now()
        print(f"\nConverting {len(lines)} filtered seeds to .png images in {img_path}")
        convert_all_ppm_to_png(lines, img_path)
        print(f"  ~{round((dt.datetime.now() - currt).total_seconds(), 4)} seconds")
    
    print("\nDone!")



if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter