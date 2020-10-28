#include "generator.h"
#include "util.h"
#include <stdio.h>

int main(int argc, char *argv[]) {

    // Parse args
    //   argv[1]: seed
    //   argv[2]: folder to save in

    if( argc != 3 ) {
        printf("Invalid arguments, choices:\n");
        printf("  argv[1]: seed");
        printf("  argv[2]: folder to save in");
        exit(1);
    }


    unsigned char biomeColours[256][3];

    // Initialize global biome table.
    initBiomes();
    // Initialize a colour map for biomes.
    initBiomeColours(biomeColours);

    // Initialize a stack of biome layers.
    LayerStack g;
    setupGenerator(&g, MC_1_16);
    // Extract the desired layer.
    Layer *layer = &g.layers[L_SHORE_16];

    int64_t seed = 1661454332289;
    int areaX = -60, areaZ = -60;
    unsigned int areaWidth = 120, areaHeight = 120;
    unsigned int scale = 4;
    unsigned int imgWidth = areaWidth*scale, imgHeight = areaHeight*scale;

    // Allocate a sufficient buffer for the biomes and for the image pixels.
    int *biomeIds = allocCache(layer, areaWidth, areaHeight);
    unsigned char *rgb = (unsigned char *) malloc(3*imgWidth*imgHeight);

    // Apply the seed only for the required layers and generate the area.
    setWorldSeed(layer, seed);
    genArea(layer, biomeIds, areaX, areaZ, areaWidth, areaHeight);

    // Map the biomes to a color buffer and save to an image.
    biomesToImage(rgb, biomeColours, biomeIds, areaWidth, areaHeight, scale, 2);
    savePPM("biomes_at_layer.ppm", rgb, imgWidth, imgHeight);

    // Clean up.
    free(biomeIds);
    free(rgb);

    return 0;
}