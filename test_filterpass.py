import util as ut
import os

filter = ["shattered_savanna", "ice_spikes", "badlands", "jungle"]
idict = ut.get_lookup_table()
enum_ints = [str(idict[key]) for key in filter]

os.system(f'./find_filtered_biomes 1 1024 extra/100k_8x0y.txt {" ".join(enum_ints)}')
