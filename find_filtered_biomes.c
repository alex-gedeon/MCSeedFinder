#include "finders.h"
#include "generator.h"
#include <stdio.h>


struct compactinfo_t {
    int64_t seedStart, seedEnd;
    unsigned int range;
    BiomeFilter filter;
    int withHut, withMonument;
    int minscale;
};

#define MAXLINELENGTH 64

static void *searchCompactBiomesThread(void *data) {
    struct compactinfo_t info = *(struct compactinfo_t *)data;
    int ax = -info.range, az = -info.range;
    int w = 2*info.range, h = 2*info.range;
    int64_t curr_seed;

    int mcversion = MC_1_14;
    LayerStack g;
    setupGenerator(&g, mcversion);
    int *cache = allocCache(&g.layers[L_VORONOI_ZOOM_1], w, h);

    for (curr_seed = info.seedStart; curr_seed != info.seedEnd; curr_seed++) {
        // if (!hasAllTemps(&g, s, 0, 0))
        //     continue;

        if (checkForBiomes(&g, L_VORONOI_ZOOM_1, cache, curr_seed, ax, az, w, h, info.filter, 1) > 0) {
            // int x, z;
            // if (info.withHut) {
            //     int r = info.range / SWAMP_HUT_CONFIG.regionSize;
            //     for (z = -r; z < r; z++) {
            //         for (x = -r; x < r; x++) {
            //             Pos p;
            //             p = getStructurePos(SWAMP_HUT_CONFIG, curr_seed, x, z, NULL);
            //             if (isViableStructurePos(Swamp_Hut, mcversion, &g, curr_seed, p.x, p.z))
            //                 goto L_hut_found;
            //         }
            //     }
            //     continue;
            //     L_hut_found:;
            // }
            // if (info.withMonument) {
            //     int r = info.range / MONUMENT_CONFIG.regionSize;
            //     for (z = -r; z < r; z++) {
            //         for (x = -r; x < r; x++) {
            //             Pos p;
            //             p = getStructurePos(MONUMENT_CONFIG, curr_seed, x, z, NULL);
            //             if (isViableStructurePos(Monument, mcversion, &g, curr_seed, p.x, p.z))
            //                 goto L_monument_found;
            //         }
            //     }
            //     continue;
            //     L_monument_found:;
            // }

            printf("%" PRId64 "\n", curr_seed);
            fflush(stdout);
        }
    }

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

    // Print line
    // int64_t temp;
    // sscanf(seed, "%" PRId64, &temp);
    // printf("%" PRId64 "\n", temp);

    // printf("%s", seed);
    return 1;
}

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
    int threads1 = atoi(argv[1]);
    int range1 = atoi(argv[2]);

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

    // Open seed file for reading
    char seed[MAXLINELENGTH];
    FILE *inFilePtr = fopen(filepath, "r");
    if(inFilePtr == NULL) {
        printf("error in opening %s\n", filepath);
    }

    // Read in one seed at a time
    while(read_file_line(inFilePtr, seed)) {
        int64_t temp;
        sscanf(seed, "%" PRId64, &temp);
    }

    



    initBiomes();

    int64_t seedStart, seedEnd;
    unsigned int threads, t, range;
    BiomeFilter filter;
    int withHut, withMonument;
    int minscale;


    // TODO: set up a customisable biome filter
    filter = setupBiomeFilter(XAND_BIOMES,
                sizeof(XAND_BIOMES)/sizeof(int));
    minscale = 1; // terminate search at this layer scale
    // TODO: simple structure filter
    // withHut = 0;
    // withMonument = 0;
    free(biome_filter);
    free(filepath);
    exit(1);

    // printf("Starting search through seeds %" PRId64 " to %" PRId64", using %u threads.\n"
    //        "Search radius = %u.\n", seedStart, seedEnd, threads, range);

    thread_id_t threadID[threads];
    struct compactinfo_t info[threads];

    // store thread information
    uint64_t seedCnt = ((uint64_t)seedEnd - (uint64_t)seedStart) / threads;
    for (t = 0; t < threads; t++) {
        info[t].seedStart = (int64_t)(seedStart + seedCnt * t);
        info[t].seedEnd = (int64_t)(seedStart + seedCnt * (t+1));
        info[t].range = range;
        info[t].filter = filter;
        // info[t].withHut = withHut;
        // info[t].withMonument = withMonument;
        info[t].minscale = minscale;
    }
    info[threads-1].seedEnd = seedEnd;

    // start threads
    for (t = 0; t < threads; ++t) {
        pthread_create(&threadID[t], NULL, searchCompactBiomesThread, (void*)&info[t]);
    }

    for (t = 0; t < threads; ++t) {
        pthread_join(threadID[t], NULL);
    }
}
