import csv

def compress(uncompressed):
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}

    w = ""
    result = []

    with open("level1_dict_compress.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["w", "k", "Output", "Index", "Symbol"])

        for c in uncompressed:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                output_code = dictionary[w]
                result.append(output_code)

                writer.writerow([w, c, output_code, dict_size, wc])

                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w:
            result.append(dictionary[w])

    return result


if __name__ == "__main__":
    data = "ABRACADABRA"
    compressed = compress(data)
    print("Compressed Output:", compressed)