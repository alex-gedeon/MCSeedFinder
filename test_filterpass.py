import util as ut
import os

filter = ["wooded_mountains", "ice_spikes", "plains"]
idict = ut.get_lookup_table()
enum_ints = [str(idict[key]) for key in filter]

os.system(f'./find_filtered_biomes 4 1024 sample_file {" ".join(enum_ints)}')
