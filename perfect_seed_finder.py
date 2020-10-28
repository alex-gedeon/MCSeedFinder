import os, sys, click, subprocess
import multiprocessing as mp
from PIL import Image


def scan_quadseeds(qx, qy, search_time, quadfile):
    process = subprocess.Popen(['./find_quadhuts', str(qx), str(qy)], stdout=open(quadfile, 'w'))
    try:
        print(f'Generating quad hut seeds at {qx * 512}, {qy * 512} for {search_time} seconds...')
        process.wait(timeout=search_time)
        print('sdaf')
    except subprocess.TimeoutExpired:
        process.kill()

    # Remove last line from file
    with open(quadfile) as qf:
        lines = qf.readlines()[:-1]
        qf.close()
    
    with open(quadfile, 'w') as qf:
        qf.writelines(lines)
        qf.close()
    print(f'Generated {len(lines)} quad witch hut seeds!')

def filter_quadseeds(quadfile):
    # Open and sort quadfile
    quads = open(quadfile).readlines()
    quads.sort()
    outfile = quadfile[:-4] + "_filtered.txt"  # remove .txt and add suffix

    # Remove existing filtered file if exists
    if os.path.exists(outfile):
        os.remove(outfile)

    # Internal function to search for seeds
    def search_seeds(queue, seedlist):
        for line in seedlist:
            if not queue.empty():
                break
            line = int(line.strip())
            os.system(f'./find_compactbiomes {int(line)} {int(line) + 1} >> {outfile}')


    # Determine number of processes and splits per process
    num_processes = mp.cpu_count()
    even_split = len(quads) // num_processes

    processpool = []
    queue = mp.Queue()
    # Create a process for each split, split into even chunks
    for idx in range(num_processes):
        a = mp.Process(target=search_seeds, args=[queue, quads[idx*even_split:idx*even_split + even_split]])
        a.start()
        processpool.append(a)

    # Attempt to join processes
    for process in processpool:
        process.join()

    print(f"Searched {even_split * num_processes} seeds!")
    return outfile

def convert_ppm_to_png(seed, folder, xsize=512, ysize=256):
    """Create png image given seed and folder."""

    # Create folder, make sure it exists
    folder = folder.strip().rstrip('/') + "/"
    if not os.path.exists(os.path.dirname(folder)):
        os.makedirs(os.path.dirname(folder))
    ppm_filepath = folder + str(seed)

    # Call c binary to generate ppm
    os.system(f'./image_generator {seed} {folder}/ {xsize} {ysize}')

    # Convert ppm to png, remove ppm to save space
    im = Image.open(f'{ppm_filepath}.ppm')
    im.save(f'{ppm_filepath}.png')
    os.remove(f'{ppm_filepath}.ppm')

@click.command()
@click.argument('qx', type=int, required=True)
@click.argument('qy', type=int, required=True)
@click.argument('search_time', type=int, default=3)
def main(qx, qy, search_time):

    ########### Step 1: Generate Seeds ###########

    # Create folder to store quad scan files
    if not os.path.exists('quad_scans/'):
        os.mkdir('quad_scans/')
    
    # Check if quadfile already exists
    quadfile = f'quad_scans/quadseeds_{qx}x{qy}y.txt'
    if not os.path.exists(quadfile):
        open(quadfile, 'x').close()
        run_scan = True
    else:
        rerun = input("File already exists, rerun anyways? (y/n): ")
        while rerun not in ['y', 'n']:
            rerun = input("File already exists, rerun anyways? (y/n): ")
        run_scan = True if rerun == 'y' else False

    # Run the scan on the quadfile if necessary
    if run_scan:
        scan_quadseeds(qx, qy, search_time, quadfile)
        
    ########### Step 2: Filter Seeds ###########

    filtered_file = filter_quadseeds(quadfile)

    ########### Step 3: Create Images ###########

    img_path = f'quad_scans/quadseeds_{qx}x{qy}y_images/'
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    with open(filtered_file) as flfile:
        for line in flfile:
            convert_ppm_to_png(line.strip(), img_path)



if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter