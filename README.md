# MCSeedFinder

Filter for seeds with quad witch huts and certain biomes efficiently.

## Current Functionality

- pipeline for running quad generator, filtering naively, generating pngs

## Ideas

- modularize functions better
- only print if told
- biome filter should only be called once per thread
- refactor filtering code significantly
  - threading fix
    - split file to pieces in python in temporary files, create quad_scans/TEMP/ directory
    - c code should spawn threads for each file, prefix specified as argv
    - make one thread a reporter thread for a progress bar
    - quad_scans/TEMP/split0.txt or something similar
    - write into quad_scans/TEMP/filtered0.txt
    - c code should potentially return value to python so it knows when its done
    - back in python, concatenate filtered files to one file, remove TEMP directory
    - convert ppm as before
  - filter fix
    - filters should be possible to define at runtime
    - idea 1: import .h file with filter than python code writes to and recompile
    - idea 2: pass in filter to c program, figure out how to parse to const int array of enum values
    - idea 2 is much harder, but much much better than idea 1. will try first
- quadfinder
  - idea 1: have a softer shutdown by having a thread checking for communication with python
  - idea 2: loop for as many seeds as specified
  - yeah idea 2 is a lot easier and better
- expand seedbank
  - should never be able to delete files, institute policty of 10m seeds minimum

- filtering
  - python
    - read in filter type from user
    - read in num to split from user
    - pre-split in python according to mp.cpu_count()
    - splits should be stored in quad_scans/tmp/{x}x{y}y_split{idx}.txt
    - spawn one process for each split
    - send master file to filter
    - how many threads to create
  - c
    - read from those for each thread, given as info.filepath
    - write into quad_scans/tmp/{x}x{y}y_split{idx}_filtered.txt
  - python
    - concatenate filtered seeds, sort, and dump into quad_scans/{x}x{y}_{filter type}_filtered.txt
  