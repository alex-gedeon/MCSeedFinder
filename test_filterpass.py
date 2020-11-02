import util as ut
import os

filter = ["wooded_mountains"]#, "ice_spikes"]#, "plains"]#, "shattered_savanna"]
idict = ut.get_lookup_table()
enum_ints = [str(idict[key]) for key in filter]

os.system(f'./find_filtered_biomes 1 1024 extra/10k_8x0y.txt {" ".join(enum_ints)}')
