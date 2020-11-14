#include "generator.h"
#include "util.h"
#include "finders.h"
#include <stdio.h>
#include <string.h>

#define MAXLINELENGTH 64
#define MAXFILEPATHLENGTH 100

struct compactinfo_t {
    char * split_filepath;
    char * output_filepath;
    int areaX;
    int areaZ;
    int reporter;
    int num_threads;
};


int read_file_line(FILE *inFilePtr, char *seed);
static void *generate_image_thread(void *data);

int main(int argc, char *argv[])
{

    // Parse args
    //   argv[1]: folder to save in
    //   argv[2]: filepath to splits
    //   argv[3]: areaX
    //   argv[4]: areaY
    //   argv[5]: num threads

    if (argc != 6)
    {
        printf("Invalid arguments, choices:\n");
        printf("  argv[1]: folder to save in\n"); // assumed to exist beforehand
        printf("  argv[2]: filepath to splits\n");
        printf("  argv[3]: areaX, ex: 512\n");
        printf("  argv[4]: areaY, ex: 256\n");
        printf("  argv[5]: num threads\n");
        exit(1);
    }


    // Get area of map
    int areaX = -1 * atoi(argv[3]), areaZ = -1 * atoi(argv[4]);

    unsigned int num_threads = atoi(argv[5]);
    thread_id_t threadID[num_threads];
    struct compactinfo_t info[num_threads];

    for(unsigned int t = 0; t < num_threads; ++t) {
        info[t].areaX = areaX;
        info[t].areaZ = areaZ;
        info[t].reporter = (t == num_threads - 1) ? 1 : 0;
        info[t].num_threads = num_threads;

        char * split_path = (char *) malloc(MAXFILEPATHLENGTH);
        strcpy(split_path, argv[2]);
        split_path[strlen(split_path) - 4] = '\0';
        strcat(split_path, "_split");

        char buffer[20];
        sprintf(buffer, "%d_filtered.txt", t);
        strcat(split_path, buffer);


        info[t].split_filepath = split_path;


        char * output_path = (char *) malloc(MAXFILEPATHLENGTH);
        strcpy(output_path, argv[1]);

        info[t].output_filepath = output_path;
    }
    // Initialize global biome table.
    initBiomes();

    for(unsigned int t = 0; t < num_threads; ++t) {
        pthread_create(&threadID[t], NULL, generate_image_thread, (void*)&info[t]);
    }
    for(unsigned int t = 0; t < num_threads; ++t) {
        pthread_join(threadID[t], NULL);
    }

    return 0;
}

int read_file_line(FILE *inFilePtr, char *seed)
{
    // Allocate buffer, clear old value
    seed[0] = '\0';

    // Read in a line
    if (fgets(seed, MAXLINELENGTH, inFilePtr) == NULL)
    {
        return 0; // If reached the end
    }

    // Check for a line being too long
    if (strchr(seed, '\n') == NULL)
    {
        // Line too long
        printf("error: line too long\n");
        exit(1);
    }

    return 1;
}

static void *generate_image_thread(void *data)
{
    struct compactinfo_t info = *(struct compactinfo_t *)data;
    unsigned int areaWidth = -2 * info.areaX, areaHeight = -2 * info.areaZ;

    unsigned char biomeColours[256][3];

    // Initialize a colour map for biomes.
    initBiomeColours(biomeColours);

    // Initialize a stack of biome layers.
    LayerStack g;
    setupGenerator(&g, MC_1_16);
    // Extract the desired layer.
    Layer *layer = &g.layers[L13_OCEAN_MIX_4]; // L13_OCEAN_MIX_4 generates frozen oceans, original: L_SHORE_16

    unsigned int scale = 1;
    unsigned int imgWidth = areaWidth * scale, imgHeight = areaHeight * scale;


    char seed[MAXLINELENGTH];
    FILE *inFilePtr = fopen(info.split_filepath, "r");
    if(inFilePtr == NULL) {
        printf("error in opening %s\n", info.split_filepath);
        exit(1);
    }

    int64_t curr_seed;
    while(read_file_line(inFilePtr, seed)) {
        sscanf(seed, "%" PRId64, &curr_seed);
        char outfile[MAXFILEPATHLENGTH];
        strcpy(outfile, info.output_filepath);
        strcat(outfile, strtok(seed, "\n"));
        strcat(outfile, ".ppm");

        // Allocate a sufficient buffer for the biomes and for the image pixels.
        int *biomeIds = allocCache(layer, areaWidth, areaHeight);
        unsigned char *rgb = (unsigned char *)malloc(3 * imgWidth * imgHeight);
        // printf("%s\n", outfile);
        // Apply the seed only for the required layers and generate the area.
        setWorldSeed(layer, curr_seed);
        genArea(layer, biomeIds, info.areaX, info.areaZ, areaWidth, areaHeight);

        // // Map the biomes to a color buffer and save to an image.
        biomesToImage(rgb, biomeColours, biomeIds, areaWidth, areaHeight, scale, 2);
        savePPM(outfile, rgb, imgWidth, imgHeight);

        // // Clean up.
        free(biomeIds);
        free(rgb);
    }

    free(info.output_filepath);
    free(info.split_filepath);
    pthread_exit(NULL);
}