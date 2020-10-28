from PIL import Image
import os


def convert_ppm_to_png(seed, folder, xsize, ysize):
    def ensure_filepath_existance(filepath):
        """Ensures that a filepath exists."""
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        if not os.path.exists(filepath):
            open(filepath, 'w').close()
    folder = folder.strip().rstrip('/') + "/"
    filepath = folder + str(seed)
    print(filepath)
    ensure_filepath_existance(filepath)
    os.system(f'./image_generator {seed} {folder}/ {xsize} {ysize}')

    im = Image.open(f'{filepath}.ppm')
    im.save(f'{filepath}.png')

convert_ppm_to_png(124, "temp2", 512, 256)