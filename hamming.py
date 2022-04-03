#
# This file contains only the functions for encoding, decoding, and correcting hamming codes.
# It does not handle boudot. It currently uses ASCII, but subtracted so that it is 5 bits.
# The functions used in this file should be more efficient and uses less code.
#

from functools import reduce



def list2string(data): return ''.join(map(str, data))



TABLE = {
	"0000": "00000000",
	"0001": "01101001", #1001011
	"0010": "10101010", #0101010
	"0011": "11000011", #1100001
	"0100": "11001100", #0011001
	"0101": "10100101", #1010010
	"0110": "01100110", #0110011
	"0111": "00001111", #1111000
	"1000": "11110000",
	"1001": "10011001", #1001100
	"1010": "01011010", #0101101
	"1011": "00110011", #1100110
	"1100": "00111100", #0011110
	"1101": "01010101", #1010101
	"1110": "10010110", #0110100
	"1111": "11111111" 
}


def hammingEncode(string, interlace=False): # 8 4 hamming code
	binStr = ""

	# The following segment is for testing
	# Boudot will be used later
	######################################
	for char in string:
		binChar = ord(char.upper()) - 59 # 5 bit ASCII
		if binChar < 32 and binChar > 0: # Skip invalid characters
			binStr += "0" * (5 - len(bin(binChar)[2:])) + bin(binChar)[2:] # Convert character to 5 bit binary number
		else:
			print("Input string contains invalid characters. Will not encode as expected. Char: " + str(binChar))
	######################################

	while len(str(binStr)) % 4 != 0: # Ensures that there is 4 bits of data
		binStr += "0"

	finalHamming = []
	if interlace:
		# TODO
		# Interlacing can increase the chance of catching multiple errors in a row aka burst errors
		# Each hamming code can only correct one error each, but when they are interlaced together, it is possible to correct multiple errors in a row
		# The decoder MUST know that the input is interlaced
		#
		# EXAMPLE:
		# 1 1 1 1 0 0 0 0 1 1 1 1
		# Would become...
		# 1 0 1 1 0 1 1 0 1 1 0 1
		# In this example, if three bits in a row were wrong, it could correct it.
		print("Interlacing is not completed yet. Please disable it.")
	else:
		for hamming in map(''.join, zip(*[iter(binStr)]*4)): # 4 bits of data per hamming code
			finalHamming.append(TABLE[hamming]) # Return hamming code

	return finalHamming # Returns array of hamming codes.


def hammingCorrect(bits): # Can only correct ONE hamming code at a time.
	# This function is where a lot of the increased efficiency comes from in this code
	# The XOR method used here is one of the most common methods for correcting hamming codes in software
	# https://youtu.be/b3NxrZOu_CE
	if int(bits) == 0:
		return bits # Empty Hamming codes are already correct, and they cannot be used in this function

	bits = [int(bit) for bit in bits] # Converts string to array, also ensures all bits are ints.
	errorPosition = reduce( # Ruturns position of error bit. Zero if no error
		lambda x, y: x ^ y, # XOR the position of all bits which are one
		[i for (i, bit) in enumerate(bits) if bit] # Assosiates each bit with an index. Only applys lambda to bits which are 1
	)

	if errorPosition != 0:
		bits[errorPosition] = int(not bits[errorPosition]) # Flip error bit

	return bits # Returns array of bits per hamming code


def hammingDecode(bits, interlace=False):
	binStr = []
	if interlace:
		# TODO
		# See comment in hammingEncode()
		print("Interlacing is not completed yet. Please disable it.")
	else:
		for hamming in map(''.join, zip(*[iter(bits)]*8)):
			binChar = list2string(hammingCorrect(hamming)) # Correct the hamming code
			try:
				binStr.append(str([data for data,hc in TABLE.items() if hc == binChar][0])) # Get the input data without parity bits
			except IndexError: # Invalid hamming code
				print("The hamming code could not be decoded correctly. Perhaps there was more than one error.")

	return binStr # Returns array of the 4 bit hamming output, NOT the 5 bit input.


#
# TODO: The following function DOES NOT WORK. However, I am keeping it in the code, as it is more scaleable
#	   than the current soulution.
#
#def hammingencoder(bits, extraParity=True):
#	maxI = 2**(len(bin(bits))-2) # Finds the highest power of 2 within the given input
#		# The -2 is because python appends a "0b" to the begining of a binary string
#	bits = int(bits) # Converts to base 10 integer from string OR binary
#	power = 1 # Skip initial parity bit, added at the end (if desired)
#	parityBits = []
#	while 2**power <= maxI: # Parity bits only land on powers of 2
#		parityBits.append(int(sum([i for i in range(bits) if i & power != 0])%2)) # Find if bit matches with parity bit
#		power *= 2
#	if extraParity: # Adds an extra parity bit in the 0 position. 



if __name__ == "__main__": # Demo
	print("\nMessage \"HELLO?\" encoded with a hamming code:")
	print(list2string(hammingEncode("HELLO?"))) # Current encoding only allows for the following characters: <=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ
	#Correct 0110011001011010010110101100001101101001010110100110100100000000
	
	WRONG = "0110011001011010010110101100101101101001010110100110100100000000"
	print("\nThe message with a 1 bit error:")
	print("0110011001011010010110101100\033[1;31m1\033[1;m01101101001010110100110100100000000")
	
	print("\nThe message corrected and decoded:")
	for char in map(''.join, zip(*[iter(list2string(hammingDecode(WRONG)))]*5)): # Split into 5 bit binary strings
		print(chr(int(char, 2) + 59), end="") # Temporary ASCII decoding
	print("\n")
