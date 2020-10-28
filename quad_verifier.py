import os, sys, time
import multiprocessing as mp


quads = open('seeds/quad_4k0k.txt').readlines()
quads.sort()

shutdown = False
def search_seeds(queue, seedlist):
    for index, line in enumerate(seedlist):
        if not queue.empty():
            break
        line = int(line.strip())
        os.system(f'./find_compactbiomes {int(line)} {int(line) + 1}')


num_threads = mp.cpu_count()
even_split = len(quads) // num_threads

processpool = []
queue = mp.Queue()
for idx in range(num_threads):
    a = mp.Process(target=search_seeds, args=[queue, quads[idx*even_split:idx*even_split + even_split]])
    a.start()
    processpool.append(a)

# input()
# queue.put(1)

for process in processpool:
    process.join()

print(f"Searched {even_split * num_threads} seeds!")
