import os, sys, click
import multiprocessing as mp
from PIL import Image

# step 1: generate seeds

# if seedfile already exists, ask user whether to regenerate
# specify how long to run seeds for
# call find_quadhuts on user inputted location
# remove last line in file
@click.command()
@click.argument('qx', type=int, required=True)
@click.argument('qy', type=int, required=True)
@click.option('--time', type=int, default=30, help='# seconds to run seed generator')
def main(qx, qy, time):

    # Create folder to store quad scan files
    if not os.path.exists('quad_scans/'):
        os.mkdir('quad_scans/')
    
    # Check if quadfile already exists
    if not os.path.exists(f'quad_scans/quadseeds_{qx}x{qy}y.txt'):
        open(f'quad_scans/quadseeds_{qx}x{qy}y.txt', 'x').close()
        run_scan = True
    else:
        rerun = input("File already exists, rerun anyways? (y/n): ")
        while rerun not in ['y', 'n']:
            rerun = input("File already exists, rerun anyways? (y/n): ")
        run_scan = True if rerun == 'y' else False



# step 2: filter seeds

# run code in quad verifier

# step 3: generate images

if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter