from LZW import LZWCoding

if __name__ == "__main__":
    filename = "thumbs_up"

    lzw = LZWCoding(filename, "image")
    lzw.decompress_image_file()
    lzw.compare_images()