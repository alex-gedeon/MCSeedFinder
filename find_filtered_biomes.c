#include "finders.h"
#include "generator.h"
#include <stdio.h>


struct compactinfo_t {
    int64_t seedStart, seedEnd;
    unsigned int range;
    BiomeFilter filter;
    int withHut, withMonument;
    int minscale;
    char * filepath;
};

#define MAXLINELENGTH 64

int read_file_line(FILE *inFilePtr, char *seed);
static void *searchCompactBiomesThread(void *data);


int main(int argc, char *argv[]) {
    // argv[0] = program name
    // argv[1] = #threads
    // argv[2] = range
    // argv[3] = filepath
    // argv[4:] = filter

    // arguments
    if (argc <= 4) {
        printf( "find_compactbiomes [seed_start] [seed_end] [threads] [range]\n"
                "\n"
                "  threads       number of threads to use [uint, default=1]\n"
                "  range         search range (in blocks) [uint, default=1024]\n"
                "  filepath      path to main file\n"
                "  filter        space separated list of biome ids\n"
        );
        exit(1);
    }

    // Read in #threads and range
    unsigned int num_threads = atoi(argv[1]);
    unsigned int search_range = atoi(argv[2]);

    // Read in filepath, remove .txt
    char * filepath = (char *) malloc(strlen(argv[3]));
    strcpy(filepath, argv[3]);
    // filepath[strlen(filepath) - 4] = '\0';

    // Read in filter
    int num_biomes = argc - 4;
    int * biome_filter = (int *) malloc(sizeof(int) * (num_biomes));
    for(int i = 4; i < argc; ++i) {
        biome_filter[i-4] = atoi(argv[i]);
    }

    initBiomes();

    // Set up filtering variables
    BiomeFilter filter;
    int minscale;
    filter = setupBiomeFilter(biome_filter, num_biomes);
    minscale = 1; // terminate search at this layer scale
    thread_id_t threadID[num_threads];
    struct compactinfo_t info[num_threads];


    // store thread information
    for (unsigned int t = 0; t < num_threads; t++) {
        info[t].range = search_range;
        info[t].filter = filter;
        info[t].minscale = minscale;
        info[t].filepath = filepath;
    }

    // start threads
    for (unsigned int t = 0; t < num_threads; ++t) {
        pthread_create(&threadID[t], NULL, searchCompactBiomesThread, (void*)&info[t]);
    }

    for (unsigned int t = 0; t < num_threads; ++t) {
        pthread_join(threadID[t], NULL);
    }
    free(biome_filter);
    free(filepath);
}

static void *searchCompactBiomesThread(void *data) {
    struct compactinfo_t info = *(struct compactinfo_t *)data;
    int ax = -info.range, az = -info.range;
    int w = 2*info.range, h = 2*info.range;

    int mcversion = MC_1_14;
    LayerStack g;
    setupGenerator(&g, mcversion);
    int *cache = allocCache(&g.layers[L_VORONOI_ZOOM_1], w, h);

    // Open seed file for reading
    char seed[MAXLINELENGTH];
    FILE *inFilePtr = fopen(info.filepath, "r");
    if(inFilePtr == NULL) {
        printf("error in opening %s\n", info.filepath);
    }    

    // Read in one seed at a time
    int count = 0;
    int hits = 0;
    while (read_file_line(inFilePtr, seed)) {
        int64_t curr_seed;
        sscanf(seed, "%" PRId64, &curr_seed);

        if (checkForBiomes(&g, L_VORONOI_ZOOM_1, cache, curr_seed, ax, az, w, h, info.filter, 1) > 0) {
            // printf("%" PRId64 "\n", curr_seed);
            // fflush(stdout);
            hits++;
        }
        count++;
    }
    printf("found %d matches from %d seeds\n", hits, count);
    free(cache);
    pthread_exit(NULL);

}

int read_file_line(FILE *inFilePtr, char *seed) {
    // Allocate buffer, clear old value
    seed[0] = '\0';

    // Read in a line
    if(fgets(seed, MAXLINELENGTH, inFilePtr) == NULL) {
        return 0; // If reached the end
    }

    // Check for a line being too long
    if(strchr(seed, '\n') == NULL) {
        // Line too long
        printf("error: line too long\n");
        exit(1);
    }

    return 1;
}
