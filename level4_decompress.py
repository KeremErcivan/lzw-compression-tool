from LZW import LZWCoding

if __name__ == "__main__":
    filename = "thumbs_up"

    lzw = LZWCoding(filename, "color_image")
    lzw.decompress_color_image_file()
    lzw.compare_color_images()