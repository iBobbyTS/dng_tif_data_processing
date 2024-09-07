import os
import tifffile
import numpy
from utils import get_exif_from_img, RAW_EXTENSIONS

input_folders = ['/Users/ibobby/Movies/temp/autopano/2023.07.21/100_0394', '/Users/ibobby/Movies/temp/autopano/2023.08.10/100_0405', '/Users/ibobby/Movies/temp/autopano/2023.08.10/100_0406', '/Users/ibobby/Movies/temp/autopano/2023.8.18/100_0439', '/Users/ibobby/Movies/temp/autopano/2023.9.2/100_0457DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.2/100_0458DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.2/100_0459DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.2/100_0460DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.9/100_0516DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.28/100_0528DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.28/100_0529DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.28/100_0535DxO', '/Users/ibobby/Movies/temp/autopano/2023.9.28/100_0544DxO', '/Users/ibobby/Movies/temp/autopano/2023.11.13/100_0679DxO', '/Users/ibobby/Movies/temp/autopano/2023.11.13/100_0681DxO', '/Users/ibobby/Movies/temp/autopano/2024.1.12/100_0706DxO', '/Users/ibobby/Movies/temp/autopano/2024.1.12/100_0733DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.13/100_0754DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.13/100_0755DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.13/100_0756DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.13/100_0757DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.13/100_0762DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.16/100_0767DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.16/100_0769DxO', '/Users/ibobby/Movies/temp/autopano/2024.3.16/100_0771DxO', '/Users/ibobby/Movies/temp/autopano/2024.4.19/100_0841DxO', '/Users/ibobby/Movies/temp/autopano/2024.5.29/100_0894DxO', '/Users/ibobby/Movies/temp/autopano/2024.5.29/100_0895DxO', '/Users/ibobby/Movies/temp/autopano/2024.5.29/100_0896DxO', '/Users/ibobby/Movies/temp/autopano/2024.6.2/100_0911DxO', '/Users/ibobby/Movies/temp/autopano/2024.6.24 日出/100_0917DxO', '/Users/ibobby/Movies/temp/autopano/2024.6.26 彩虹/100_0921DxO', '/Users/ibobby/Movies/temp/autopano/2024.7.24/100_0942DxO', '/Users/ibobby/Movies/temp/autopano/2024.7.24/100_0944DxO', '/Users/ibobby/Movies/temp/autopano/2024.7.24/100_0945DxO']
output_folder = None
change_size = False


def find_all(data, pattern):
    found = []
    start = 0
    while True:
        # Find the pattern in the data starting from 'start'
        index = data.find(pattern, start)
        if index == -1:
            break
        else:
            found.append(index)
            # Update start to the position immediately after the found pattern
            start = index + len(pattern)
    return found


def cvt_dng_to_tif(dng_path, tif_path):
    exif_output = get_exif_from_img(dng_path, ('BitsPerSample', 'ImageWidth', 'ImageHeight'))
    bits_per_sample, width, height = exif_output
    bits_per_sample = bits_per_sample.split(' ')
    byte_per_channel = int(bits_per_sample[0])//8
    channel_per_sample = len(bits_per_sample)
    file = open(dng_path, 'rb')
    file_size = os.path.getsize(dng_path)
    data_size = width * height * byte_per_channel * channel_per_sample
    offset = file_size - data_size
    file.seek(offset)
    size = width * height * byte_per_channel * channel_per_sample
    content = file.read(size)
    file.close()
    array = numpy.frombuffer(content, dtype=numpy.uint16)
    image_data = array.reshape((height, width, channel_per_sample))
    tifffile.imwrite(tif_path, image_data)
    os.system(f'exiftool -tagsFromFile "{dng_path}" -all:all -overwrite_original "{tif_path}"')


for input_folder in input_folders:
    # if output_folder is None:
    if True:
        output_folder = os.path.join(input_folder, 'tiff')
    os.makedirs(output_folder, exist_ok=True)
    files = os.listdir(input_folder)
    for file in files:
        if file.lower().endswith(RAW_EXTENSIONS):
            name, _ = os.path.splitext(file)
            cvt_dng_to_tif(os.path.join(input_folder, file), os.path.join(output_folder, name+'.tiff'))
