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
    int reporter;
    int num_threads;
};

#define MAXLINELENGTH 64
#define MAXFILEPATHLENGTH 100

int read_file_line(FILE *inFilePtr, char *seed);
static void *searchCompactBiomesThread(void *data);


int main(int argc, char *argv[]) {
    // argv[0] = program name
    // argv[1] = #threads
    // argv[2] = range
    // argv[3] = filepath
    // argv[4] = file size
    // argv[4:] = filter
    int THREADIDX = 1;
    int RANGEIDX = 2;
    int FILEPATHIDX = 3;
    // int FILESIZEIDX = 4;
    int NUMPARAMS = 4;

    // arguments
    if (argc <= 4) {
        printf( "find_compactbiomes [seed_start] [seed_end] [threads] [range]\n"
                "\n"
                "  threads       number of threads to use [uint, default=1]\n"
                "  range         search range (in blocks) [uint, default=1024]\n"
                "  filepath      path to main file\n"
                // "  file size     size of file to filter\n"
                "  filter        space separated list of biome ids\n"
        );
        exit(1);
    }

    // Read in #threads and range
    unsigned int num_threads = atoi(argv[THREADIDX]);
    unsigned int search_range = atoi(argv[RANGEIDX]);

    // Read in filepath, remove .txt
    char * filepath = (char *) malloc(MAXFILEPATHLENGTH);
    strcpy(filepath, argv[FILEPATHIDX]);
    filepath[strlen(argv[FILEPATHIDX]) - 4] = '\0';
    strcat(filepath, "_split");

    // Read in filter
    int num_biomes = argc - NUMPARAMS;
    int * biome_filter = (int *) malloc(sizeof(int) * (num_biomes));
    for(int i = NUMPARAMS; i < argc; ++i) {
        biome_filter[i-NUMPARAMS] = atoi(argv[i]);
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

        // Make new filepath object
        char * dest_filepath = (char *) malloc(MAXFILEPATHLENGTH);
        strcpy(dest_filepath, filepath);

        // Add value of t to buffer and filepath extension
        char buffer[20];
        sprintf(buffer, "%d.txt", t);

        // Add buffer to dest path
        strcat(dest_filepath, buffer);
        
        // Add filepath to struct, will be freed inside thread function
        info[t].filepath = dest_filepath;
        info[t].reporter = (t == num_threads - 1) ? 1 : 0;
        info[t].num_threads = num_threads;

    }
    // exit(1);

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
        exit(1);
    }

    char outfilepath[MAXFILEPATHLENGTH];
    strcpy(outfilepath, info.filepath);

    for(int i = 0; i < MAXFILEPATHLENGTH; ++i) {
        if(outfilepath[i] == '.') {
            outfilepath[i] = '\0';
            strcat(outfilepath, "_filtered.txt");
            break;
        }
    }

    FILE *outFileptr = fopen(outfilepath, "w");
    if(outFileptr == NULL) {
        printf("error in opening outfile");
        exit(1);
    }

    // Find number of lines in file
    char buf[MAXLINELENGTH];
    int num_lines = 0;
    while(fgets(buf, MAXLINELENGTH, inFilePtr) != NULL) {
        num_lines++;
    }
    rewind(inFilePtr);

    // Read in one seed at a time
    int count = 0;
    int last_perc = -1;
    int hits = 0;
    int64_t curr_seed;
    while (read_file_line(inFilePtr, seed)) {
        if(info.reporter && (int)((double)count/num_lines * 100) > last_perc) {
            last_perc = (int)((double)count/num_lines * 100);
            printf("\rProgress: %d%%", last_perc);
            fflush(stdout);
        }

        sscanf(seed, "%" PRId64, &curr_seed);

        if (checkForBiomes(&g, L_VORONOI_ZOOM_1, cache, curr_seed, ax, az, w, h, info.filter, 1) > 0) {
            // printf("%" PRId64 "\n", curr_seed);
            // fflush(stdout);
            fprintf(outFileptr, "%" PRId64 "\n", curr_seed);
            hits++;
            if(info.num_threads * hits > 1000) {
                printf("Hit 1000, stopping\n");
                break;
            }
        }
        count++;
    }
    if(info.reporter) {
        printf("\rProgress: 100%%\n");
        printf("\nFound %d matches - approximately %d total - from %d/%d seeds\n", hits, info.num_threads * hits, count, count * info.num_threads);
    }
    free(cache);
    free(info.filepath);
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
