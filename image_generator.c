#include "generator.h"
#include "util.h"
#include <stdio.h>
#include <string.h>

int64_t S64(const char *s) {
  int64_t i;
  char c ;
  int scanned = sscanf(s, "%" SCNd64 "%c", &i, &c);
  if (scanned == 1) return i;
  if (scanned > 1) {
    // TBD about extra data found
    return i;
    }
  // TBD failed to scan;  
  return 0;  
}

int main(int argc, char *argv[]) {

    // Parse args
    //   argv[1]: seed
    //   argv[2]: folder to save in

    if( argc != 5 ) {
        printf("Invalid arguments, choices:\n");
        printf("  argv[1]: seed\n");
        printf("  argv[2]: folder to save in\n");  // assumed to exist beforehand
        printf("  argv[3]: areaX, ex: 512\n");
        printf("  argv[4]: areaY, ex: 256\n");
        exit(1);
    }

    // Parse command line arguments
    char massive_string[1000] = "";  // Probably a better way to do this
    strcat(massive_string, argv[2]);
    strcat(massive_string, argv[1]);
    strcat(massive_string, ".ppm");
    int64_t seed = S64(argv[1]);

    // Get area of map
    int areaX = -1 * atoi(argv[3]), areaZ = -1 * atoi(argv[4]);
    unsigned int areaWidth = -2 * areaX, areaHeight = -2 * areaZ;

    unsigned char biomeColours[256][3];

    // Initialize global biome table.
    initBiomes();
    // Initialize a colour map for biomes.
    initBiomeColours(biomeColours);

    // Initialize a stack of biome layers.
    LayerStack g;
    setupGenerator(&g, MC_1_16);
    // Extract the desired layer.
    Layer *layer = &g.layers[L13_OCEAN_MIX_4];  // L13_OCEAN_MIX_4 generates frozen oceans, original: L_SHORE_16

    unsigned int scale = 1;
    unsigned int imgWidth = areaWidth*scale, imgHeight = areaHeight*scale;

    // Allocate a sufficient buffer for the biomes and for the image pixels.
    int *biomeIds = allocCache(layer, areaWidth, areaHeight);
    unsigned char *rgb = (unsigned char *) malloc(3*imgWidth*imgHeight);

    // Apply the seed only for the required layers and generate the area.
    setWorldSeed(layer, seed);
    genArea(layer, biomeIds, areaX, areaZ, areaWidth, areaHeight);

    // Map the biomes to a color buffer and save to an image.
    biomesToImage(rgb, biomeColours, biomeIds, areaWidth, areaHeight, scale, 2);
    savePPM(massive_string, rgb, imgWidth, imgHeight);

    // Clean up.
    free(biomeIds);
    free(rgb);

    return 0;
}