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

    # Read in user's filter
    user_filter, filter_id = ut.get_filter(given_filter=biome_filter)
    idict = ut.get_lookup_table()
    biome_ids = [str(idict[key]) for key in user_filter]
    print(f"Scanning with {', '.join(user_filter[:])}")

    search_coords = ut.get_search_coords()
    ut.ensure_scan_structure(filter_id, search_range)
    for s_idx, s_coord in enumerate(search_coords):
        print(
            f"Starting search in {s_coord}, no. {s_idx + 1}/{len(search_coords)} total")
        master_filepath = f"seed_bank/quadbank_{s_coord}.txt"
        ut.make_splits(master_filepath, s_coord)

        # Scan master file in C and aggregate results
        ut.run_biome_scan(biome_ids, s_coord, search_range)
        export_file = ut.aggregate_scan(filter_id, s_coord, search_range)

        # Generate images of minecraft world
        ut.generate_images(export_file)

    all_path = f"quad_scans/filter{filter_id}_{search_range}r/all/"
    print("\nResults:")
    os.system(
        f'echo "Found" $(find {all_path}* | wc -l) "matches out of" $(cat seed_bank/* | wc -l) "total"')


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
