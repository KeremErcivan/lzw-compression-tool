from LZW import LZWCoding

if __name__ == "__main__":
    filename = "thumbs_up"

    lzw = LZWCoding(filename, "image")
    lzw.compress_image_file()