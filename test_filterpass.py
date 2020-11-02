import util as ut
import os

filter = ["jungle", "shattered_savanna", "ice_spikes", "badlands"]
idict = ut.get_lookup_table()
enum_ints = sorted([idict[key] for key in filter])
enum_ints = [str(val) for val in enum_ints]

os.system(f'./find_filtered_biomes 1 1024 extra/100k_8x0y.txt {" ".join(enum_ints)}')
