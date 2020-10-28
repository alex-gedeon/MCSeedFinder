from PIL import Image
import os


def convert_ppm_to_png(seed, folder, xsize=512, ysize=256):
    """Create png image given seed and folder."""

    # Create folder, make sure it exists
    folder = folder.strip().rstrip('/') + "/"
    if not os.path.exists(os.path.dirname(folder)):
        os.makedirs(os.path.dirname(folder))
    ppm_filepath = folder + str(seed)

    print(folder)

    # Call c binary to generate ppm
    os.system(f'./image_generator {seed} {folder}/ {xsize} {ysize}')

    # Convert ppm to png, remove ppm to save space
    im = Image.open(f'{ppm_filepath}.ppm')
    im.save(f'{ppm_filepath}.png')
    os.remove(f'{ppm_filepath}.ppm')

convert_ppm_to_png(124, "quad_scans/qddadsffdsafdsad/")
