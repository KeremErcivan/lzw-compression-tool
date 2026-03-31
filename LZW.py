import os  # the os module is used for file and directory operations
import math  # the math module provides access to mathematical functions

# A class that implements the LZW compression and decompression algorithms as
# well as the necessary utility methods for text files.
# ------------------------------------------------------------------------------
class LZWCoding:
   # A constructor with two input parameters
   # ---------------------------------------------------------------------------
   def __init__(self, filename, data_type):
      # use the input parameters to set the instance variables
      self.filename = filename
      self.data_type = data_type   # e.g., 'text'
      # initialize the code length as None 
      # (the actual value is determined based on the compressed data)
      self.codelength = None

   # A method that compresses the contents of a text file to a binary output file 
   # and returns the path of the output file.
   # ---------------------------------------------------------------------------
   def compress_text_file(self):
      # get the current directory where this program is placed
      current_directory = os.path.dirname(os.path.realpath(__file__))
      # build the path of the input file
      input_file = self.filename + '.txt'
      input_path = current_directory + '/' + input_file
      # build the path of the output file
      output_file = self.filename + '_compressed.bin'
      output_path = current_directory + '/' + output_file

      # read the contents of the input file
      in_file = open(input_path, 'r')
      text = in_file.read()
      in_file.close()

      # encode the text by using the LZW compression algorithm
      encoded_text_as_integers = self.encode(text)
      # get the binary string that corresponds to the compressed text
      encoded_text = self.int_list_to_binary_string(encoded_text_as_integers)
      # add the code length info to the beginning of the encoded text
      # (the compressed data must contain everything needed to decompress it)
      encoded_text = self.add_code_length_info(encoded_text)
      # perform padding if needed
      padded_encoded_text = self.pad_encoded_data(encoded_text)
      # convert the resulting string into a byte array
      byte_array = self.get_byte_array(padded_encoded_text)

      # write the bytes in the byte array to the output file (compressed file)
      out_file = open(output_path, 'wb')   # binary mode
      out_file.write(bytes(byte_array))
      out_file.close()

      # notify the user that the compression process is finished
      print(input_file + ' is compressed into ' + output_file + '.')
      # compute and print the details of the compression process
      uncompressed_size = len(text)
      print('Original Size: ' + '{:,d}'.format(uncompressed_size) + ' bytes')
      print('Code Length: ' + str(self.codelength))
      compressed_size = len(byte_array)
      print('Compressed Size: ' + '{:,d}'.format(compressed_size) + ' bytes')
      compression_ratio = compressed_size / uncompressed_size
      print('Compression Ratio: ' + '{:.2f}'.format(compression_ratio))

      # return the path of the output file
      return output_path
   
   # A method that encodes a text input into a list of integer values by using
   # the LZW compression algorithm and returns the resulting list.
   # ---------------------------------------------------------------------------
   def encode(self, uncompressed_data):
      # build the initial dictionary by mapping the characters in the extended 
      # ASCII table to their indexes
      dict_size = 256
      dictionary = {chr(i): i for i in range(dict_size)}

      # perform the LZW compression algorithm
      w = ''   # initialize a variable to store the current sequence
      result = []   # initialize a list to store the encoded values to output
      # iterate over each item (a character for text files) in the input data
      for k in uncompressed_data:
         # keep forming a new sequence until it is not in the dictionary
         wk = w + k
         if wk in dictionary:   # if wk exists in the dictionary
            w = wk   # update the sequence by adding the current item
         else:   # otherwise
            # add the code for w (the longest sequence found in the dictionary)
            # to the list that stores the encoded values
            result.append(dictionary[w])
            # add wk (the new sequence) to the dictionary
            dictionary[wk] = dict_size
            dict_size += 1
            # reset w to the current character
            w = k
      # add the code for the remaining sequence to the list 
      # that stores the encoded values (integer codes)
      if w:
         result.append(dictionary[w])
      
      # set the code length for compressing the encoded values based on the input 
      # data by using the size of the resulting dictionary (note that real-world 
      # LZW implementations often grow the code length dynamically)
      self.codelength = math.ceil(math.log2(len(dictionary)))

      # return the encoded values (a list of integer dictionary values)
      return result

   # A method that converts the integer list returned by the compress method
   # into a binary string and returns the resulting string.
   # ---------------------------------------------------------------------------
   def int_list_to_binary_string(self, int_list):
      # create a list to store the bits of the binary string 
      # (using a list is more efficient than repeatedly concatenating strings)
      bits = []
      # for each integer in the input list
      for num in int_list:
         # convert each integer code to its codelength-bit binary representation
         for n in range(self.codelength):
            if num & (1 << (self.codelength - 1 - n)):
               bits.append('1')
            else:
               bits.append('0')
      # return the result as a string
      return ''.join(bits)

   # A method that adds the code length to the beginning of the binary string
   # that corresponds to the compressed data and returns the resulting string.
   # (the compressed data should contain everything needed to decompress it)
   # ---------------------------------------------------------------------------
   def add_code_length_info(self, bitstring):
      # create a binary string that stores the code length as a byte
      codelength_info = '{0:08b}'.format(self.codelength)
      # add the code length info to the beginning of the given binary string
      bitstring = codelength_info + bitstring
      # return the resulting binary string
      return bitstring

   # A method for adding zeros to the binary string (the compressed data)
   # to make the length of the string a multiple of 8.
   # (This is necessary to be able to write the values to the file as bytes.)
   # ---------------------------------------------------------------------------
   def pad_encoded_data(self, encoded_data):
      # compute the number of the extra bits to add
      if len(encoded_data) % 8 != 0:
         extra_bits = 8 - len(encoded_data) % 8
         # add zeros to the end (padding)
         for i in range(extra_bits):
            encoded_data += '0'
      else:   # no need to add zeros
         extra_bits = 0
      # add a byte that stores the number of added zeros to the beginning of
      # the encoded data (this is necessary because the decompressor must know
      # how many padding bits were added artificially in order to remove them)
      padding_info = '{0:08b}'.format(extra_bits)
      encoded_data = padding_info + encoded_data
      # return the resulting string after padding
      return encoded_data

   # A method that converts the padded binary string to a byte array and returns 
   # the resulting array. 
   # (This byte array will be written to a file to store the compressed data.)
   # ---------------------------------------------------------------------------
   def get_byte_array(self, padded_encoded_data):
      # the length of the padded binary string must be a multiple of 8
      if (len(padded_encoded_data) % 8 != 0):
         print('The compressed data is not padded properly!')
         exit(0)
      # create a byte array
      b = bytearray()
      # append the padded binary string byte by byte
      for i in range(0, len(padded_encoded_data), 8):
         byte = padded_encoded_data[i : i + 8]
         b.append(int(byte, 2))
      # return the resulting byte array
      return b

   # A method that reads the contents of a compressed binary file, performs
   # decompression and writes the decompressed output to a text file.
   # ---------------------------------------------------------------------------
   def decompress_text_file(self):
      # get the current directory where this program is placed
      current_directory = os.path.dirname(os.path.realpath(__file__))
      # build the path of the input file
      input_file = self.filename + '_compressed.bin'
      input_path = current_directory + '/' + input_file
      # build the path of the output file
      output_file = self.filename + '_decompressed.txt'
      output_path = current_directory + '/' + output_file

      # read the contents of the input file
      in_file = open(input_path, 'rb')   # binary mode
      compressed_data = in_file.read()
      in_file.close()

      # create a binary string from the bytes read from the compressed file
      from io import StringIO   # using StringIO for efficiency
      bit_string = StringIO()
      for byte in compressed_data:
         bits = bin(byte)[2:].rjust(8, '0')
         bit_string.write(bits)
      bit_string = bit_string.getvalue()

      # remove padding
      bit_string = self.remove_padding(bit_string)
      # remove the code length info and set the instance variable codelength
      bit_string = self.extract_code_length_info(bit_string)
      # convert the compressed binary string to a list of integer values
      encoded_text = self.binary_string_to_int_list(bit_string)
      # decode the encoded text by using the LZW decompression algorithm
      decompressed_text = self.decode(encoded_text)

      # write the decompression output to the output file
      out_file = open(output_path, 'w')
      out_file.write(decompressed_text)
      out_file.close()

      # notify the user that the decompression process is finished
      print(input_file + ' is decompressed into ' + output_file + '.')
      
      # return the path of the output file
      return output_path

   # A method to remove the padding info and the added zeros from the compressed
   # binary string and return the resulting string.
   def remove_padding(self, padded_encoded_data):
      # extract the padding info (the first 8 bits of the input string)
      padding_info = padded_encoded_data[:8]
      encoded_data = padded_encoded_data[8:]
      # remove the extra zeros (if any) and return the resulting string
      extra_padding = int(padding_info, 2) 
      if extra_padding != 0:
         encoded_data = encoded_data[:-1 * extra_padding]
      return encoded_data

   # A method to extract the code length info from the compressed binary string
   # and return the resulting string.
   # ---------------------------------------------------------------------------
   def extract_code_length_info(self, bitstring):
      # the first 8 bits of the input string contain the code length info
      codelength_info = bitstring[:8]
      self.codelength = int(codelength_info, 2)
      # return the resulting binary string after removing the code length info
      return bitstring[8:]

   # A method that converts the compressed binary string to a list of int codes
   # and returns the resulting list.
   # ---------------------------------------------------------------------------
   def binary_string_to_int_list(self, bitstring):
      # generate the list of integer codes from the binary string
      int_codes = []
      # for each compressed value (a binary string with codelength bits)
      for bits in range(0, len(bitstring), self.codelength):
         # compute the integer code and add it to the list
         int_code = int(bitstring[bits: bits + self.codelength], 2)
         int_codes.append(int_code)
      # return the resulting list
      return int_codes
   
   # A method that decodes a list of encoded integer values into a string (text) 
   # by using the LZW decompression algorithm and returns the resulting output.
   # ---------------------------------------------------------------------------
   def decode(self, encoded_values):
      # build the initial dictionary by mapping the index values in the extended 
      # ASCII table to their corresponding characters
      dict_size = 256
      dictionary = {i: chr(i) for i in range(dict_size)}

      # perform the LZW decompression algorithm
      # ------------------------------------------------------------------------
      from io import StringIO   # using StringIO for efficiency
      result = StringIO()
      # initialize w as the character corresponding to the first encoded value
      # in the list and add this character to the output string
      w = chr(encoded_values.pop(0))
      result.write(w)
      # iterate over each encoded value in the list
      for k in encoded_values:
         # if the value is in the dictionary
         if k in dictionary:
            # retrieve the corresponding string
            entry = dictionary[k]
         # if the value is equal to the current dictionary size
         elif k == dict_size:
            # construct the entry
            entry = w + w[0]   # a special case where the entry is formed
         # if k is invalid (not in the dictionary and not equal to dict_size)
         else:
            # raise an error
            raise ValueError('Bad compressed k: %s' % k)
         # add the entry to the output
         result.write(entry)
         # w + the first character of the entry is added to the dictionary 
         # as a new sequence
         dictionary[dict_size] = w + entry[0]
         dict_size += 1
         # update w to the current entry
         w = entry
      
      # return the resulting output (the decompressed string/text)
      return result.getvalue()
   
   # A method that encodes grayscale image pixel values into integer codes.
   # In image compression, each grayscale pixel value (0-255) is treated as a symbol.
   # Tuples are used instead of strings so that pixel sequences can be stored in the LZW dictionary.
   def encode_image(self, pixel_values):
      dict_size = 256
      dictionary = {(i,): i for i in range(dict_size)}

      w = ()
      result = []

      for pixel in pixel_values:
         wk = w + (pixel,)
         if wk in dictionary:
            w = wk
         else:
            if w:
               result.append(dictionary[w])
            dictionary[wk] = dict_size
            dict_size += 1
            w = (pixel,)

      if w:
         result.append(dictionary[w])

      self.codelength = math.ceil(math.log2(len(dictionary)))
      return result

   # Adds width, height and code length info to the compressed binary string.
   # Width, height, and code length are stored in the compressed file
   # so that the image can be reconstructed during decompression without external information.  
   def add_image_info(self, bitstring, width, height):
      width_info = '{0:016b}'.format(width)
      height_info = '{0:016b}'.format(height)
      codelength_info = '{0:08b}'.format(self.codelength)
      return width_info + height_info + codelength_info + bitstring

   # Extracts width, height and code length info from the compressed binary string.
   def extract_image_info(self, bitstring):
      width = int(bitstring[:16], 2)
      height = int(bitstring[16:32], 2)
      self.codelength = int(bitstring[32:40], 2)
      return width, height, bitstring[40:]

   # A method that decodes integer codes into grayscale pixel values.
   def decode_image(self, encoded_values):
      dict_size = 256
      dictionary = {i: (i,) for i in range(dict_size)}

      w = dictionary[encoded_values.pop(0)]
      result = list(w)

      for k in encoded_values:
         if k in dictionary:
            entry = dictionary[k]
         elif k == dict_size:
            entry = w + (w[0],)
         else:
            raise ValueError('Bad compressed k: %s' % k)

         result.extend(entry)
         dictionary[dict_size] = w + (entry[0],)
         dict_size += 1
         w = entry

      return result

   # Computes entropy for grayscale image pixels.
   def calculate_image_entropy(self, pixel_values):
      total = len(pixel_values)
      freq = {}

      for pixel in pixel_values:
         if pixel in freq:
            freq[pixel] += 1
         else:
            freq[pixel] = 1

      entropy = 0
      for count in freq.values():
         p = count / total
         entropy -= p * math.log2(p)

      return entropy

   # Computes average code length.
   def calculate_average_code_length(self, encoded_values):
      if len(encoded_values) == 0:
         return 0
      total_bits = len(encoded_values) * self.codelength
      return total_bits / len(encoded_values)

   # Compresses a grayscale image into a binary file.
   def compress_image_file(self):
      from image_tools import readPILimg, color2gray, PIL2np

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '.bmp'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_compressed.bin'
      output_path = os.path.join(current_directory, output_file)

      img = readPILimg(input_path)
      gray_img = color2gray(img)
      gray_array = PIL2np(gray_img)

      height, width = gray_array.shape
      pixel_values = gray_array.flatten().tolist()

      encoded_image_as_integers = self.encode_image(pixel_values)
      encoded_image = self.int_list_to_binary_string(encoded_image_as_integers)
      encoded_image = self.add_image_info(encoded_image, width, height)
      padded_encoded_image = self.pad_encoded_data(encoded_image)
      byte_array = self.get_byte_array(padded_encoded_image)

      out_file = open(output_path, 'wb')
      out_file.write(bytes(byte_array))
      out_file.close()

      print(input_file + ' is compressed into ' + output_file + '.')
      original_size = len(pixel_values)
      print('Original Size: ' + '{:,d}'.format(original_size) + ' bytes')
      print('Width:', width)
      print('Height:', height)
      print('Code Length:', self.codelength)

      compressed_size = len(byte_array)
      print('Compressed Size: ' + '{:,d}'.format(compressed_size) + ' bytes')

      compression_ratio = compressed_size / original_size
      print('Compression Ratio: ' + '{:.4f}'.format(compression_ratio))

      entropy = self.calculate_image_entropy(pixel_values)
      print('Entropy:', round(entropy, 4))

      avg_code_length = self.calculate_average_code_length(encoded_image_as_integers)
      print('Average Code Length:', round(avg_code_length, 4))

      return output_path

   # Decompresses a binary file into a grayscale image.
   def decompress_image_file(self):
      from io import StringIO
      import numpy as np
      from image_tools import np2PIL

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '_compressed.bin'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_decompressed.bmp'
      output_path = os.path.join(current_directory, output_file)

      in_file = open(input_path, 'rb')
      compressed_data = in_file.read()
      in_file.close()

      bit_string = StringIO()
      for byte in compressed_data:
         bits = bin(byte)[2:].rjust(8, '0')
         bit_string.write(bits)
      bit_string = bit_string.getvalue()

      bit_string = self.remove_padding(bit_string)
      width, height, bit_string = self.extract_image_info(bit_string)
      encoded_image = self.binary_string_to_int_list(bit_string)
      decompressed_pixels = self.decode_image(encoded_image)

      img_array = np.array(decompressed_pixels, dtype=np.uint8).reshape((height, width))
      img = np2PIL(img_array)
      img.save(output_path)

      print(input_file + ' is decompressed into ' + output_file + '.')
      print('Width:', width)
      print('Height:', height)

      return output_path

   # Compares original image (converted to grayscale) and decompressed image.
   def compare_images(self):
      from image_tools import readPILimg, color2gray, PIL2np
      import numpy as np

      current_directory = os.path.dirname(os.path.realpath(__file__))

      original_path = os.path.join(current_directory, self.filename + '.bmp')
      decompressed_path = os.path.join(current_directory, self.filename + '_decompressed.bmp')

      original_img = readPILimg(original_path)
      original_gray = color2gray(original_img)
      decompressed_img = readPILimg(decompressed_path)

      original_array = PIL2np(original_gray)
      decompressed_array = PIL2np(decompressed_img)

      if np.array_equal(original_array, decompressed_array):
         print('Images are identical')
      else:
         print('Images are different')

   # Creates the difference image from a grayscale image array.
   # The difference image is formed by using vertical differences in the first column
   # and horizontal differences for the remaining pixels in each row.
   # This usually reduces redundancy and improves compression.
   def create_difference_image(self, gray_array):
      import numpy as np

      height, width = gray_array.shape
      diff_array = np.zeros((height, width), dtype=int)

      diff_array[0][0] = int(gray_array[0][0])

      for i in range(1, height):
         diff_array[i][0] = int(gray_array[i][0]) - int(gray_array[i - 1][0])

      for i in range(height):
         for j in range(1, width):
            diff_array[i][j] = int(gray_array[i][j]) - int(gray_array[i][j - 1])

      return diff_array

   # Restores the original grayscale image from the difference image.
   # This method reconstructs the original grayscale image by reversing
   # the same vertical and horizontal difference operations used in compression. 
   def restore_image_from_difference(self, diff_array):
      import numpy as np

      height, width = diff_array.shape
      restored_array = np.zeros((height, width), dtype=int)

      restored_array[0][0] = int(diff_array[0][0])

      for i in range(1, height):
         restored_array[i][0] = int(diff_array[i][0]) + int(restored_array[i - 1][0])

      for i in range(height):
         for j in range(1, width):
            restored_array[i][j] = int(diff_array[i][j]) + int(restored_array[i][j - 1])

      return restored_array

   # Encodes difference image values into integer codes using LZW.
   # Difference image values may be negative, so the initial dictionary
   # must cover the range from -255 to 255 instead of only 0 to 255.
   def encode_difference_image(self, diff_values):
      diff_symbols = list(range(-255, 256))
      dict_size = len(diff_symbols)
      dictionary = {(value,): i for i, value in enumerate(diff_symbols)}

      w = ()
      result = []

      for value in diff_values:
         wk = w + (value,)
         if wk in dictionary:
            w = wk
         else:
            if w:
               result.append(dictionary[w])
            dictionary[wk] = dict_size
            dict_size += 1
            w = (value,)

      if w:
         result.append(dictionary[w])

      self.codelength = math.ceil(math.log2(len(dictionary)))
      return result

   # Decodes LZW codes back into difference image values.
   def decode_difference_image(self, encoded_values):
      diff_symbols = list(range(-255, 256))
      dict_size = len(diff_symbols)
      dictionary = {i: (value,) for i, value in enumerate(diff_symbols)}

      w = dictionary[encoded_values.pop(0)]
      result = list(w)

      for k in encoded_values:
         if k in dictionary:
            entry = dictionary[k]
         elif k == dict_size:
            entry = w + (w[0],)
         else:
            raise ValueError('Bad compressed k: %s' % k)

         result.extend(entry)
         dictionary[dict_size] = w + (entry[0],)
         dict_size += 1
         w = entry

      return result

   # Computes entropy for any integer-valued image sequence.
   def calculate_sequence_entropy(self, values):
      total = len(values)
      freq = {}

      for value in values:
         if value in freq:
            freq[value] += 1
         else:
            freq[value] = 1

      entropy = 0
      for count in freq.values():
         p = count / total
         entropy -= p * math.log2(p)

      return entropy

   # Compresses grayscale image using difference image + LZW.
   # In Level 3, the grayscale image is first converted into a difference image,
   # then the resulting difference values are compressed with LZW.
   def compress_difference_image_file(self):
      from image_tools import readPILimg, color2gray, PIL2np

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '.bmp'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_difference_compressed.bin'
      output_path = os.path.join(current_directory, output_file)

      img = readPILimg(input_path)
      gray_img = color2gray(img)
      gray_array = PIL2np(gray_img)

      height, width = gray_array.shape

      diff_array = self.create_difference_image(gray_array)
      diff_values = diff_array.flatten().tolist()
      original_values = gray_array.flatten().tolist()

      encoded_diff_as_integers = self.encode_difference_image(diff_values)
      encoded_diff = self.int_list_to_binary_string(encoded_diff_as_integers)
      encoded_diff = self.add_image_info(encoded_diff, width, height)
      padded_encoded_diff = self.pad_encoded_data(encoded_diff)
      byte_array = self.get_byte_array(padded_encoded_diff)

      out_file = open(output_path, 'wb')
      out_file.write(bytes(byte_array))
      out_file.close()

      print(input_file + ' is compressed into ' + output_file + '.')
      original_size = len(original_values)
      print('Original Size: ' + '{:,d}'.format(original_size) + ' bytes')
      print('Width:', width)
      print('Height:', height)
      print('Code Length:', self.codelength)

      compressed_size = len(byte_array)
      print('Compressed Size: ' + '{:,d}'.format(compressed_size) + ' bytes')

      compression_ratio = compressed_size / original_size
      print('Compression Ratio: ' + '{:.4f}'.format(compression_ratio))

      image_entropy = self.calculate_sequence_entropy(original_values)
      diff_entropy = self.calculate_sequence_entropy(diff_values)
      print('Image Entropy:', round(image_entropy, 4))
      print('Difference Image Entropy:', round(diff_entropy, 4))

      avg_code_length = self.calculate_average_code_length(encoded_diff_as_integers)
      print('Average Code Length:', round(avg_code_length, 4))

      return output_path

   # Decompresses binary data into a restored grayscale image using difference image.
   def decompress_difference_image_file(self):
      from io import StringIO
      import numpy as np
      from image_tools import np2PIL

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '_difference_compressed.bin'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_difference_decompressed.bmp'
      output_path = os.path.join(current_directory, output_file)

      in_file = open(input_path, 'rb')
      compressed_data = in_file.read()
      in_file.close()

      bit_string = StringIO()
      for byte in compressed_data:
         bits = bin(byte)[2:].rjust(8, '0')
         bit_string.write(bits)
      bit_string = bit_string.getvalue()

      bit_string = self.remove_padding(bit_string)
      width, height, bit_string = self.extract_image_info(bit_string)
      encoded_diff = self.binary_string_to_int_list(bit_string)
      decompressed_diff_values = self.decode_difference_image(encoded_diff)

      diff_array = np.array(decompressed_diff_values, dtype=int).reshape((height, width))
      restored_array = self.restore_image_from_difference(diff_array)

      restored_array = np.clip(restored_array, 0, 255)
      img = np2PIL(restored_array)
      img.save(output_path)

      print(input_file + ' is decompressed into ' + output_file + '.')
      print('Width:', width)
      print('Height:', height)

      return output_path

   # Compares original grayscale image with difference-decompressed image.
   def compare_difference_images(self):
      from image_tools import readPILimg, color2gray, PIL2np
      import numpy as np

      current_directory = os.path.dirname(os.path.realpath(__file__))

      original_path = os.path.join(current_directory, self.filename + '.bmp')
      decompressed_path = os.path.join(current_directory, self.filename + '_difference_decompressed.bmp')

      original_img = readPILimg(original_path)
      original_gray = color2gray(original_img)
      decompressed_img = readPILimg(decompressed_path)

      original_array = PIL2np(original_gray)
      decompressed_array = PIL2np(decompressed_img)

      if np.array_equal(original_array, decompressed_array):
         print('Images are identical')
      else:
         print('Images are different')

      # -----------------------------------------------------------
   # LEVEL 4: RGB IMAGE METHODS
   # -----------------------------------------------------------

   # Converts integer codes into a binary string using a given code length.
   # RGB channels may produce different dictionary sizes,
   # so each channel may require a different code length.
   def int_list_to_binary_string_with_length(self, int_list, code_length):
      bits = []
      for num in int_list:
         for n in range(code_length):
            if num & (1 << (code_length - 1 - n)):
               bits.append('1')
            else:
               bits.append('0')
      return ''.join(bits)

   # Converts a binary string into integer codes using a given code length.
   def binary_string_to_int_list_with_length(self, bitstring, code_length):
      int_codes = []
      for i in range(0, len(bitstring), code_length):
         code_bits = bitstring[i:i + code_length]
         if len(code_bits) == code_length:
            int_codes.append(int(code_bits, 2))
      return int_codes

   # Adds RGB image info to the beginning of the compressed binary string.
   # For RGB compression, the compressed red, green, and blue streams are stored
   # in a single binary file together with their individual code lengths and bit lengths. 
   def add_color_image_info(self, red_bits, green_bits, blue_bits,
                            width, height,
                            red_code_length, green_code_length, blue_code_length):

      width_info = '{0:016b}'.format(width)
      height_info = '{0:016b}'.format(height)

      red_code_info = '{0:08b}'.format(red_code_length)
      green_code_info = '{0:08b}'.format(green_code_length)
      blue_code_info = '{0:08b}'.format(blue_code_length)

      red_length_info = '{0:032b}'.format(len(red_bits))
      green_length_info = '{0:032b}'.format(len(green_bits))
      blue_length_info = '{0:032b}'.format(len(blue_bits))

      header = (
         width_info + height_info +
         red_code_info + green_code_info + blue_code_info +
         red_length_info + green_length_info + blue_length_info
      )

      return header + red_bits + green_bits + blue_bits

   # Extracts RGB image info from the compressed binary string.
   def extract_color_image_info(self, bitstring):
      width = int(bitstring[:16], 2)
      height = int(bitstring[16:32], 2)

      red_code_length = int(bitstring[32:40], 2)
      green_code_length = int(bitstring[40:48], 2)
      blue_code_length = int(bitstring[48:56], 2)

      red_length = int(bitstring[56:88], 2)
      green_length = int(bitstring[88:120], 2)
      blue_length = int(bitstring[120:152], 2)

      start = 152
      red_bits = bitstring[start:start + red_length]
      start += red_length

      green_bits = bitstring[start:start + green_length]
      start += green_length

      blue_bits = bitstring[start:start + blue_length]

      return (width, height,
              red_code_length, green_code_length, blue_code_length,
              red_bits, green_bits, blue_bits)

   # Compresses an RGB image into a binary file.
   # The RGB image is split into red, green, and blue channels,
   # and each channel is compressed independently using grayscale-style LZW encoding.
   def compress_color_image_file(self):
      from image_tools import readPILimg, PIL2np

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '.bmp'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_color_compressed.bin'
      output_path = os.path.join(current_directory, output_file)

      img = readPILimg(input_path).convert('RGB')
      img_array = PIL2np(img)

      height, width, channels = img_array.shape

      red_values = img_array[:, :, 0].flatten().tolist()
      green_values = img_array[:, :, 1].flatten().tolist()
      blue_values = img_array[:, :, 2].flatten().tolist()

      encoded_red = self.encode_image(red_values)
      red_code_length = self.codelength

      encoded_green = self.encode_image(green_values)
      green_code_length = self.codelength

      encoded_blue = self.encode_image(blue_values)
      blue_code_length = self.codelength

      red_bits = self.int_list_to_binary_string_with_length(encoded_red, red_code_length)
      green_bits = self.int_list_to_binary_string_with_length(encoded_green, green_code_length)
      blue_bits = self.int_list_to_binary_string_with_length(encoded_blue, blue_code_length)

      encoded_data = self.add_color_image_info(
         red_bits, green_bits, blue_bits,
         width, height,
         red_code_length, green_code_length, blue_code_length
      )

      padded_encoded_data = self.pad_encoded_data(encoded_data)
      byte_array = self.get_byte_array(padded_encoded_data)

      out_file = open(output_path, 'wb')
      out_file.write(bytes(byte_array))
      out_file.close()

      print(input_file + ' is compressed into ' + output_file + '.')
      original_size = len(red_values) + len(green_values) + len(blue_values)
      print('Original Size: ' + '{:,d}'.format(original_size) + ' bytes')
      print('Width:', width)
      print('Height:', height)
      print('Red Code Length:', red_code_length)
      print('Green Code Length:', green_code_length)
      print('Blue Code Length:', blue_code_length)

      compressed_size = len(byte_array)
      print('Compressed Size: ' + '{:,d}'.format(compressed_size) + ' bytes')

      compression_ratio = compressed_size / original_size
      print('Compression Ratio: ' + '{:.4f}'.format(compression_ratio))

      red_entropy = self.calculate_image_entropy(red_values)
      green_entropy = self.calculate_image_entropy(green_values)
      blue_entropy = self.calculate_image_entropy(blue_values)

      print('Red Entropy:', round(red_entropy, 4))
      print('Green Entropy:', round(green_entropy, 4))
      print('Blue Entropy:', round(blue_entropy, 4))

      total_bits = (
         len(encoded_red) * red_code_length +
         len(encoded_green) * green_code_length +
         len(encoded_blue) * blue_code_length
      )
      total_codes = len(encoded_red) + len(encoded_green) + len(encoded_blue)

      avg_code_length = total_bits / total_codes
      print('Average Code Length:', round(avg_code_length, 4))

      return output_path

   # Decompresses a binary file into an RGB image.
   # During decompression, each RGB channel is decoded separately
   # and then the three reconstructed channels are merged back into a color image.
   def decompress_color_image_file(self):
      from io import StringIO
      import numpy as np
      from image_tools import np2PIL

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '_color_compressed.bin'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_color_decompressed.bmp'
      output_path = os.path.join(current_directory, output_file)

      in_file = open(input_path, 'rb')
      compressed_data = in_file.read()
      in_file.close()

      bit_string = StringIO()
      for byte in compressed_data:
         bits = bin(byte)[2:].rjust(8, '0')
         bit_string.write(bits)
      bit_string = bit_string.getvalue()

      bit_string = self.remove_padding(bit_string)

      (width, height,
       red_code_length, green_code_length, blue_code_length,
       red_bits, green_bits, blue_bits) = self.extract_color_image_info(bit_string)

      encoded_red = self.binary_string_to_int_list_with_length(red_bits, red_code_length)
      encoded_green = self.binary_string_to_int_list_with_length(green_bits, green_code_length)
      encoded_blue = self.binary_string_to_int_list_with_length(blue_bits, blue_code_length)

      red_values = self.decode_image(encoded_red)
      green_values = self.decode_image(encoded_green)
      blue_values = self.decode_image(encoded_blue)

      red_array = np.array(red_values, dtype=np.uint8).reshape((height, width))
      green_array = np.array(green_values, dtype=np.uint8).reshape((height, width))
      blue_array = np.array(blue_values, dtype=np.uint8).reshape((height, width))

      rgb_array = np.stack((red_array, green_array, blue_array), axis=2)

      img = np2PIL(rgb_array)
      img.save(output_path)

      print(input_file + ' is decompressed into ' + output_file + '.')
      print('Width:', width)
      print('Height:', height)

      return output_path

   # Compares original RGB image and decompressed RGB image.
   def compare_color_images(self):
      from image_tools import readPILimg, PIL2np
      import numpy as np

      current_directory = os.path.dirname(os.path.realpath(__file__))

      original_path = os.path.join(current_directory, self.filename + '.bmp')
      decompressed_path = os.path.join(current_directory, self.filename + '_color_decompressed.bmp')

      original_img = readPILimg(original_path).convert('RGB')
      decompressed_img = readPILimg(decompressed_path).convert('RGB')

      original_array = PIL2np(original_img)
      decompressed_array = PIL2np(decompressed_img)

      if np.array_equal(original_array, decompressed_array):
         print('Images are identical')
      else:
         print('Images are different')
      # -----------------------------------------------------------
   # LEVEL 5: RGB DIFFERENCE IMAGE METHODS
   # -----------------------------------------------------------

   # Compresses an RGB image using difference images for each channel.
   # In Level 5, difference coding is applied separately to each RGB channel
   # before LZW compression in order to reduce entropy and improve compression performance.
   def compress_color_difference_image_file(self):
      from image_tools import readPILimg, PIL2np

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '.bmp'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_color_difference_compressed.bin'
      output_path = os.path.join(current_directory, output_file)

      img = readPILimg(input_path).convert('RGB')
      img_array = PIL2np(img)

      height, width, channels = img_array.shape

      red_array = img_array[:, :, 0]
      green_array = img_array[:, :, 1]
      blue_array = img_array[:, :, 2]

      red_diff = self.create_difference_image(red_array)
      green_diff = self.create_difference_image(green_array)
      blue_diff = self.create_difference_image(blue_array)

      red_values = red_array.flatten().tolist()
      green_values = green_array.flatten().tolist()
      blue_values = blue_array.flatten().tolist()

      red_diff_values = red_diff.flatten().tolist()
      green_diff_values = green_diff.flatten().tolist()
      blue_diff_values = blue_diff.flatten().tolist()

      encoded_red = self.encode_difference_image(red_diff_values)
      red_code_length = self.codelength

      encoded_green = self.encode_difference_image(green_diff_values)
      green_code_length = self.codelength

      encoded_blue = self.encode_difference_image(blue_diff_values)
      blue_code_length = self.codelength

      red_bits = self.int_list_to_binary_string_with_length(encoded_red, red_code_length)
      green_bits = self.int_list_to_binary_string_with_length(encoded_green, green_code_length)
      blue_bits = self.int_list_to_binary_string_with_length(encoded_blue, blue_code_length)

      encoded_data = self.add_color_image_info(
         red_bits, green_bits, blue_bits,
         width, height,
         red_code_length, green_code_length, blue_code_length
      )

      padded_encoded_data = self.pad_encoded_data(encoded_data)
      byte_array = self.get_byte_array(padded_encoded_data)

      out_file = open(output_path, 'wb')
      out_file.write(bytes(byte_array))
      out_file.close()

      print(input_file + ' is compressed into ' + output_file + '.')
      original_size = len(red_values) + len(green_values) + len(blue_values)
      print('Original Size: ' + '{:,d}'.format(original_size) + ' bytes')
      print('Width:', width)
      print('Height:', height)
      print('Red Code Length:', red_code_length)
      print('Green Code Length:', green_code_length)
      print('Blue Code Length:', blue_code_length)

      compressed_size = len(byte_array)
      print('Compressed Size: ' + '{:,d}'.format(compressed_size) + ' bytes')

      compression_ratio = compressed_size / original_size
      print('Compression Ratio: ' + '{:.4f}'.format(compression_ratio))

      red_entropy = self.calculate_image_entropy(red_values)
      green_entropy = self.calculate_image_entropy(green_values)
      blue_entropy = self.calculate_image_entropy(blue_values)

      red_diff_entropy = self.calculate_sequence_entropy(red_diff_values)
      green_diff_entropy = self.calculate_sequence_entropy(green_diff_values)
      blue_diff_entropy = self.calculate_sequence_entropy(blue_diff_values)

      print('Red Entropy:', round(red_entropy, 4))
      print('Green Entropy:', round(green_entropy, 4))
      print('Blue Entropy:', round(blue_entropy, 4))

      print('Red Difference Entropy:', round(red_diff_entropy, 4))
      print('Green Difference Entropy:', round(green_diff_entropy, 4))
      print('Blue Difference Entropy:', round(blue_diff_entropy, 4))

      total_bits = (
         len(encoded_red) * red_code_length +
         len(encoded_green) * green_code_length +
         len(encoded_blue) * blue_code_length
      )
      total_codes = len(encoded_red) + len(encoded_green) + len(encoded_blue)

      avg_code_length = total_bits / total_codes
      print('Average Code Length:', round(avg_code_length, 4))

      return output_path

   # Decompresses RGB difference-image compressed data into an RGB image.
   # Each RGB difference channel is decoded first, then the original channel values
   # are restored by reversing the difference-image process, and finally the channels are merged.
   def decompress_color_difference_image_file(self):
      from io import StringIO
      import numpy as np
      from image_tools import np2PIL

      current_directory = os.path.dirname(os.path.realpath(__file__))
      input_file = self.filename + '_color_difference_compressed.bin'
      input_path = os.path.join(current_directory, input_file)

      output_file = self.filename + '_color_difference_decompressed.bmp'
      output_path = os.path.join(current_directory, output_file)

      in_file = open(input_path, 'rb')
      compressed_data = in_file.read()
      in_file.close()

      bit_string = StringIO()
      for byte in compressed_data:
         bits = bin(byte)[2:].rjust(8, '0')
         bit_string.write(bits)
      bit_string = bit_string.getvalue()

      bit_string = self.remove_padding(bit_string)

      (width, height,
       red_code_length, green_code_length, blue_code_length,
       red_bits, green_bits, blue_bits) = self.extract_color_image_info(bit_string)

      encoded_red = self.binary_string_to_int_list_with_length(red_bits, red_code_length)
      encoded_green = self.binary_string_to_int_list_with_length(green_bits, green_code_length)
      encoded_blue = self.binary_string_to_int_list_with_length(blue_bits, blue_code_length)

      red_diff_values = self.decode_difference_image(encoded_red)
      green_diff_values = self.decode_difference_image(encoded_green)
      blue_diff_values = self.decode_difference_image(encoded_blue)

      red_diff_array = np.array(red_diff_values, dtype=int).reshape((height, width))
      green_diff_array = np.array(green_diff_values, dtype=int).reshape((height, width))
      blue_diff_array = np.array(blue_diff_values, dtype=int).reshape((height, width))

      red_array = self.restore_image_from_difference(red_diff_array)
      green_array = self.restore_image_from_difference(green_diff_array)
      blue_array = self.restore_image_from_difference(blue_diff_array)

      red_array = np.clip(red_array, 0, 255).astype(np.uint8)
      green_array = np.clip(green_array, 0, 255).astype(np.uint8)
      blue_array = np.clip(blue_array, 0, 255).astype(np.uint8)

      rgb_array = np.stack((red_array, green_array, blue_array), axis=2)

      img = np2PIL(rgb_array)
      img.save(output_path)

      print(input_file + ' is decompressed into ' + output_file + '.')
      print('Width:', width)
      print('Height:', height)

      return output_path

   # Compares original RGB image and difference-decompressed RGB image.
   def compare_color_difference_images(self):
      from image_tools import readPILimg, PIL2np
      import numpy as np

      current_directory = os.path.dirname(os.path.realpath(__file__))

      original_path = os.path.join(current_directory, self.filename + '.bmp')
      decompressed_path = os.path.join(current_directory, self.filename + '_color_difference_decompressed.bmp')

      original_img = readPILimg(original_path).convert('RGB')
      decompressed_img = readPILimg(decompressed_path).convert('RGB')

      original_array = PIL2np(original_img)
      decompressed_array = PIL2np(decompressed_img)

      if np.array_equal(original_array, decompressed_array):
         print('Images are identical')
      else:
         print('Images are different')