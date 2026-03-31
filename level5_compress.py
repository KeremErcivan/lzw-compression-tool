from LZW import LZWCoding

if __name__ == "__main__":
    filename = "thumbs_up"

    lzw = LZWCoding(filename, "color_difference_image")
    lzw.compress_color_difference_image_file()