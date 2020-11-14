CC      = gcc
AR      = ar
ARFLAGS = cr
override LDFLAGS = -lm
override CFLAGS += -Wall -fwrapv

ifeq ($(OS),Windows_NT)
	override CFLAGS += -D_WIN32
	RM = del
else
	override LDFLAGS += -lX11 -pthread
	#RM = rm
endif

.PHONY : all release debug libcubiomes clean

all: release generate_images

debug: CFLAGS += -DDEBUG -O0 -ggdb3
debug: libcubiomes find_quadhuts image_generator find_filtered_biomes
release: CFLAGS += -O3 -march=native
release: libcubiomes find_quadhuts image_generator find_filtered_biomes

libcubiomes: CFLAGS += -fPIC
libcubiomes: layers.o generator.o finders.o util.o
	$(AR) $(ARFLAGS) libcubiomes.a $^

find_quadhuts: find_quadhuts.o layers.o generator.o finders.o 
	$(CC) -o $@ $^ $(LDFLAGS)

find_quadhuts.o: find_quadhuts.c
	$(CC) -c $(CFLAGS) $<

image_generator: image_generator.o layers.o generator.o finders.o util.o
	$(CC) -o $@ $^ $(LDFLAGS)

finders.o: finders.c finders.h
	$(CC) -c $(CFLAGS) $<

generator.o: generator.c generator.h
	$(CC) -c $(CFLAGS) $<

layers.o: layers.c layers.h
	$(CC) -c $(CFLAGS) $<

util.o: util.c util.h
	$(CC) -c $(CFLAGS) $<

image_generator.o: image_generator.c util.h generator.h
	$(CC) -c $(CFLAGS) $<
	
find_filtered_biomes.o: find_filtered_biomes.c generator.h
	$(CC) -c $(CFLAGS) $<

find_filtered_biomes: find_filtered_biomes.o layers.o generator.o finders.o
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	$(RM) *.o libcubiomes.a find_quadhuts find_compactbiomes image_generator find_filtered_biomes

generate_images.o: generate_images.c util.h generator.h
	$(CC) -c $(CFLAGS) $<

generate_images: generate_images.o layers.o generator.o finders.o util.o
	$(CC) -o $@ $^ $(LDFLAGS)