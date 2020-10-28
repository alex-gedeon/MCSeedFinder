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

def filter_quadseeds():
    pass

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


        


# step 2: filter seeds

# run code in quad verifier

# step 3: generate images

if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter