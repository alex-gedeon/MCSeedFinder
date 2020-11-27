# MCSeedFinder

Filter for seeds with quad witch huts and user-specified biomes efficiently, heavily inspired by https://github.com/Cubitect/cubiomes.

## Usage

The bulk of the work is done through the interface provided by ```filter_seeds.py```, interfacing with the C programs compiled with ```make -j```.

Example usage:

```bash
make -j
./find_quadhuts 8 0 > quad_bank/quad_bank_8x0y.txt &
sleep 60 && kill %1
echo "jungle, shattered_savanna, ice_spikes, warm_ocean, mushroom_fields" >> biome_filters.txt
python3 filter_seeds.py --biome_filter=0 --search_range=1024
```

### Arguments

This script takes in two optional arguments: search range, and a biome filter. The search range is set to a default of 1024, and specifies the distance to search in both the X and Z directions around the origin. The biome filter is given as a labeled entry in ```biome_filters.txt```, where a ```", "``` separated list of biomes is defined for each line, starting with a label ```{label}:```, with biomes named as per https://minecraft.gamepedia.com/Biome/ID, such as ```0: jungle, shattered_savanna, ice_spikes, warm_ocean, mushroom_fields```.

### Quad Witch Hut Seed Generation

The script ```filter_seeds.py``` will expect quad witch huts seeds to already be pre-computed in the default folder ```quad_bank/```. This folder should contain files in the form of ```quadbank_{x coord}x{z coord}z.txt```, where the coordinates refer to the coordinates, scaled by a factor of 512, of the location of the quad witch huts. This is due to the fact that the program ```./find_quadhuts``` takes in two arguments for the X and Z location to search for quad witch huts in, scaled by a factor of 512. This means that if you want to generate quad witch huts at (4096, 0), you should supply the arguments ```8 0``` to this program. Since these seeds need to be generated before filtering, and often take many hours to get a sizeable amount of, it is recommended to have several searches running at once. A selection of pre-generated quad witch hut seeds can be found here: https://drive.google.com/drive/folders/1bVCnAEXKUbUD3amtHRxZhA3gzVeT3D6Q.

For example, a search at coordinates (4096, 0), or (8, 0) in the programs coordinates, could be done as follows:
```./find_quadhuts 8 0 > quad_bank/quadbank_8x0y.txt &```

Since this program does not currently have functionality to stop the search elegantly, it may be killed while writing a seed to the file, so ensure that the last line is removed before filtering through it.

### Biome Filtering

Once filters are defined, and once quad witch hut seeds have been computed, they can be filtered for specific biomes. For each pre-computed seed file, the script ```filter_seeds.py``` will first make as many splits of it as there are cores on your machine, in ```biome_scans/tmp/```.

The location of these files will be passed in to ```./find_filtered_biomes``` for a multi-threaded scan over each split. Matches will be stored in the tmp directory by the C program, and then concatenated together to the output directory correlated with the arguments of the scan. For coordinates of (8, 0) with filter 0 and a search range of 1024, the concatenated file of all matching seeds will be stored in ```biome_scans/filter0_1024r/8x0y/8x0y_filtered.txt```.

Next, the matched seeds will be generated into first .ppm images, and then to .png to save space. They will be both in the ```/generated/``` folder for each coordinate folder, as well as in the ```/all/``` folder for each filter for ease of viewing. Using the previous example, they would appear in ```biome_scans/filter0_1024r/8x0y/generated/``` and ```biome_scans/filter0_1024r/all/```, with names in the form of ```{matching seed}.png```.

### Conclusion

With this script you should be able to find quad witch hut seeds at given areas, filter around the origin for specific biomes, and visualize the results far more easily than before.
