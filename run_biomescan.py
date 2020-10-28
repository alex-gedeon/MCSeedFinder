import os, sys, threading

with open('seeds/max_seeds_scanned.txt', 'r') as seedfile:
    lines = seedfile.readlines()
max_seen = int(lines[0])

shutdown = False
def run_scans(num_threads, max_seen):
    increment = int(1e7)
    start_seed = max_seen
    while not shutdown:
        print(f"Searching from {max_seen // int(1e6)}m to {(max_seen + increment) // int(1e6)}m")
        os.system(f'./find_compactbiomes {max_seen} {max_seen + increment} {num_threads} >> seeds/biome_seedlog.txt')
        max_seen += increment
    print(f"Total seeds scanned: {(max_seen - start_seed) // int(1e6)}m")
    os.system(f'echo {max_seen} > seeds/max_seeds_scanned.txt')

num_threads = sys.argv[1]

a = threading.Thread(target=run_scans, args=[num_threads, max_seen])
a.start()
input()
print("Shutting down")
shutdown = True
a.join()
