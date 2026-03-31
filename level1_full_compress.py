from LZW import LZWCoding
import math
from collections import Counter

def calculate_entropy(text):
    total = len(text)
    freq = Counter(text)
    entropy = 0
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

if __name__ == "__main__":
    filename = "sample"

    # Entropy için text'i okuyalım
    with open(filename + ".txt", "r") as f:
        text = f.read()

    entropy = calculate_entropy(text)
    print("Entropy:", round(entropy, 4))

    # Full compression pipeline
    lzw = LZWCoding(filename, "text")
    lzw.compress_text_file()