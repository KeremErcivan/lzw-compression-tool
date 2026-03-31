import csv
from io import StringIO

def decompress(compressed):

    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}

    result = StringIO()

    with open("level1_dict_decompress.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["w", "k", "Output", "Index", "Symbol"])

        w = chr(compressed.pop(0))
        result.write(w)

        for k in compressed:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError("Bad compressed k: %s" % k)

            result.write(entry)

            writer.writerow([w, k, entry, dict_size, w + entry[0]])

            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            w = entry

    return result.getvalue()


if __name__ == "__main__":
    compressed_data = [65, 66, 82, 65, 67, 65, 68, 256, 258]
    decompressed = decompress(compressed_data)
    print("Decompressed Output:", decompressed)