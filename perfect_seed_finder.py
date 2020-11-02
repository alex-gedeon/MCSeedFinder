import os
import click
import time
from shutil import rmtree
import datetime as dt

import util as ut

# def parse_run_scan(force, delete_if_run=False):
#     pass


@click.command()
@click.argument('qx', type=int, required=True)
@click.argument('qy', type=int, required=True)
@click.argument('search_time', type=int, default=5)
@click.option('--force', type=str, default="default")
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
    else:
        if force == "default":
            rerun = input("Quadfile already exists, rerun anyways? (y/n): ")
            while rerun not in ['y', 'n']:
                rerun = input("Quadfile already exists, rerun anyways? (y/n): ")
            run_scan = True if rerun == 'y' else False
        else:
            run_scan = False

    # Run the scan on the quadfile if necessary
    if run_scan:
        ut.scan_quadseeds(qx, qy, search_time, quadfile)

    ########### Step 2: Filter Seeds ###########

    filtered_file = quadfile[:-4] + \
        "_filtered.txt"  # remove .txt and add suffix

    # Remove existing filtered file if exists
    run_scan = True
    if os.path.exists(filtered_file):
        if force == "default":
            rerun = input("Filter quadfile already exists, rerun anyways? (y/n): ")
            while rerun not in ['y', 'n']:
                rerun = input(
                    "Filter quadfile already exists, rerun anyways? (y/n): ")
            run_scan = True if rerun == 'y' else False
        else:
            run_scan = False
    if run_scan:
        currt = dt.datetime.now()
        ut.filter_quadseeds(quadfile, filtered_file)
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
        print(
            f"\nConverting {len(lines)} filtered seeds to .png images in {img_path}")
        ut.convert_all_ppm_to_png(lines, img_path)
        print(f"  ~{round((dt.datetime.now() - currt).total_seconds(), 4)} seconds")

    print("\nDone!")


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
