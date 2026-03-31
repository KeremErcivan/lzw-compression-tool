from LZW import LZWCoding

if __name__ == "__main__":
    filename = "thumbs_up"

    lzw = LZWCoding(filename, "difference_image")
    lzw.decompress_difference_image_file()
    lzw.compare_difference_images()