from LZW import LZWCoding

if __name__ == "__main__":
    filename = "sample"

    lzw = LZWCoding(filename, "text")
    lzw.decompress_text_file()

    # Dosyaları karşılaştır
    with open(filename + ".txt", "r") as f1:
        original = f1.read()

    with open(filename + "_decompressed.txt", "r") as f2:
        decompressed = f2.read()

    if original == decompressed:
        print("Files are identical")
    else:
        print("Files are different")