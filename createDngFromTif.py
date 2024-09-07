import os
import tifffile
import numpy
from utils import get_exif_from_img, RAW_EXTENSIONS

tif_file = '/Users/ibobby/Pictures/autopano/[Group 0]-PANO0001-DNG-24-uncompressed_PANO0009-DNG-5-uncompressed-9 images.tif.tiff'
dng_ref = '/Users/ibobby/Pictures/pano/PANO0001-DNG-24-uncompressed.dng'
output_dng = None
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


def copy_tif_to_dng(tif_path, dng_path, output_dng_path):
    # Read dng meta
    dng_exif_output = get_exif_from_img(dng_path, ('BitsPerSample', 'ImageWidth', 'ImageHeight'))
    dng_bits_per_sample, dng_width, dng_height = dng_exif_output
    dng_bits_per_sample = dng_bits_per_sample.split(' ')
    dng_byte_per_channel = int(dng_bits_per_sample[0])//8
    dng_channel_per_sample = len(dng_bits_per_sample)
    file_size = os.path.getsize(dng_path)
    dng_data_size = dng_width * dng_height * dng_byte_per_channel * dng_channel_per_sample
    offset = file_size - dng_data_size
    dng_file = open(dng_path, 'rb')
    header = dng_file.read(offset)
    dng_file.close()
    # Get tif meta
    tif_exif_output = get_exif_from_img(tif_path, ('BitsPerSample', 'ImageWidth', 'ImageHeight'))
    tif_bits_per_sample, tif_width, tif_height = tif_exif_output
    tif_bits_per_sample = tif_bits_per_sample.split(' ')
    tif_byte_per_channel = int(tif_bits_per_sample[0]) // 8
    tif_channel_per_sample = len(tif_bits_per_sample)
    tif_data_size = tif_width * tif_height * tif_byte_per_channel * tif_channel_per_sample
    # Change width, height in dng header
    widths = find_all(header, numpy.array((dng_width,), dtype=numpy.int32).tobytes())
    heights = find_all(header, numpy.array((dng_height,), dtype=numpy.int32).tobytes())
    data_sizes = find_all(header, numpy.array((dng_data_size,), dtype=numpy.int32).tobytes())
    header = bytearray(header)
    for w in widths:
        header[w:w+4] = numpy.array((tif_width,), dtype=numpy.int32).tobytes()
    for h in heights:
        header[h:h+4] = numpy.array((tif_height,), dtype=numpy.int32).tobytes()
    for d in data_sizes:
        header[d:d+4] = numpy.array((tif_data_size,), dtype=numpy.int32).tobytes()
    # read tif image data
    image_data = tifffile.imread(tif_path)
    output_dng = open(output_dng_path, 'wb')
    output_dng.write(header)
    output_dng.write(image_data.tobytes())
    output_dng.close()


if output_dng is None:
    output_dng, _ = os.path.splitext(tif_file)
    output_dng += '.dng'

print(output_dng)
copy_tif_to_dng(tif_file, dng_ref, output_dng)
