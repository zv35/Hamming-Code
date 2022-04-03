import textwrap
import sys

def list2string(data):
	return ''.join(map(str, data))

# https://en.wikipedia.org/wiki/Baudot_code#ITA2
## International telegraphy alphabet No.2 (Baudot-Murray code)
## LSB on righht; code element:543*21
SIGNS = {
	"FS": "11011",
	"LS": "11111",
	"SP": "00100", # take fron ER
}

LETTERS = {
	"A": "00011",
	"B": "11001",
	"C": "01110",
	"D": "01001",
	"E": "00001",
	"F": "01101",
	"G": "11010",
	"H": "10100",
	"I": "00110",
	"J": "01011",
	"K": "01111",
	"L": "10010",
	"M": "11100",
	"N": "01100",
	"O": "11000",
	"P": "10110",
	"Q": "10111",
	"R": "01010",
	"S": "00101",
	"T": "10000",
	"U": "00111",
	"V": "11110",
	"W": "10011",
	"X": "11101",
	"Y": "10101",
	"Z": "10001"
}

FIGURES = {
	"0": "10110",
	"1": "10111",
	"2": "10011",
	"3": "00001",
	"4": "01010",
	"5": "10000",
	"6": "10101",
	"7": "00111",
	"8": "00110",
	"9": "11000",
	"-": "00011",
	"?": "11001",
	":": "01110",
	"(": "01111",
	")": "10010",
	".": "11100",
	",": "01100",
	"'": "00101",
	"=": "11110",
	"/": "11101",
	"+": "10001",
	"!": "01101",
    	"&": "11010"
}


def encodeBaudot(info):

	rst = []
	text = info.upper().split()

	LC = 0 	# letter count
	FC = 0 	# figure

	for word in text:
		s = []
		for letter in word:

			if letter in LETTERS:
				if LC > 0:
					s.append(LETTERS[letter])
					#LC += 1
				else:
					s.append(SIGNS['LS'])
					s.append(LETTERS[letter])
					LC += 1	
					FC = 0

			if letter in FIGURES:
				if FC > 0:
					s.append(FIGURES[letter])
				else:
					s.append(SIGNS['FS'])
					s.append(FIGURES[letter])
					FC += 1
					LC = 0
		
		rst.extend(s)
		rst.append(SIGNS['SP'])

	return rst[:-1]


def originaldecodeBaudot(s):
	
	WORDS = []

	flag_L = False
	flag_F = False

	data = textwrap.wrap(s, 5)

	for sign in data:

		if sign == SIGNS['LS']:
			flag_L = True
			flag_F = False
		
		elif sign == SIGNS['FS']:
			flag_F = True
			flag_L = False
			
		elif sign == SIGNS['SP']:
			WORDS.extend(' ')
		else:
			if flag_L:
				if sign in SIGNS.values():
					if sign == SIGNS['FS']:
						flag_L = False
						flag_F = True
					else:
						flag_F = False
						flag_L = True
				else:
					for letter, code in LETTERS.items():
						if code == sign:
							WORDS.extend(letter)

			elif flag_F:
				if sign in SIGNS.values():
					if sign == SIGNS['LS']:
						flag_F = False
						flag_L = True
					else:
						flag_F = True
						flag_L = False
				else:
					for figure, code in FIGURES.items():
						if code == sign:
							WORDS.extend(figure)

	return list2string(WORDS)

# https://en.wikipedia.org/wiki/Hamming(7,4)
zero = '0'
one = '1'

TABLE = {
	"0000": "0000000",
	"1000": "1110000",
	"0100": "1001100", #0011001
	"1100": "0111100", #0011110
	"0010": "0101010", #0101010
	"1010": "1011010", #0101101
	"0110": "1100110", #0110011
	"1110": "0010110", #0110100
	"0001": "1101001", #1001011
	"1001": "0011001", #1001100
	"0101": "0100101", #1010010
	"1101": "1010101", #1010101
	"0011": "1000011", #1100001
	"1011": "0110011", #1100110
	"0111": "0001111", #1111000
	"1111": "1111111" 
}

def Hammingencoder(s, span=4):

	en = []

	if len(s) % span == 0:
		
		data = tuple(textwrap.wrap(s, span))

		for datum in data:
			for origin, code in TABLE.items():
				if origin == datum:
					en.extend(code)	

	else:
		remainder = len(s) % span
		main = s[:-remainder]
		sub = s[-remainder:]
		data = tuple(textwrap.wrap(main, span))
		
		for datum in data:
			for origin, code in TABLE.items():
				if origin == datum:
					#print datum, code
					en.extend(code)

		en.extend(sub)

	return list2string(en)


def Hammingdecoder(s, span=7):

	de = []
	index_zero = s.index(one*7)
	string = s[index_zero:len(s)]
	strings = tuple(textwrap.wrap(string, span))
	for i in strings:
	
		if len(i) == span:
			for origin, code in TABLE.items():
	
				if code == i:
					de.extend(origin)
	
		else:
			de.extend(i)	

	return list2string(de)


def Hammingcorrector(s, num=7):

	rst = []
	#p = (0,1,3)
	#d = (2,4,5,6)
	p1 = (0,2,4,6)
	p2 = (1,2,5,6)
	p4 = (3,4,5,6)
    
	begin = 0
	string = s[begin:len(s)]
	strings = tuple(textwrap.wrap(string, num))

	for i in strings:

		if len(i) == num:

			t4 = parity(i, p4)
			t2 = parity(i, p2)
			t1 = parity(i, p1)

		if t4+t2+t1 != zero*3:
			index = (int(t4+t2+t1, 2)) - 1
			sub = [e for e in i]
			if sub[index] == zero:
				sub[index] = 1
			else:
				sub[index] = 0
			rst.extend(sub)

		else:
			rst.extend(i)
	return list2string(rst)

def parity(s, indicies):
    alist = [s[i] for i in indicies]
    sub = ''.join(alist)
    return str(str.count(sub, '1') % 2) 



text = "the";
info = list2string(encodeBaudot(text));
en = Hammingencoder(info);
wrong = '11111110110100010101011100001101001';
crct = Hammingcorrector(wrong);
print(crct)
de = Hammingdecoder('11111110111100010101011100001101001');
print(originaldecodeBaudot(de));

"""
## Test encoding and decoding
file = open("plain text.txt")
text = file.read().replace("\n", " ");
file.close(); 
info = list2string(encodeBaudot(text));
file2 = open("binary.txt","w")
file2.write(info);
file2.close;
file2 = open("binary.txt")
info2 = file2.read().replace("\n", " ");
file2.close(); 
b = originaldecodeBaudot(info2);
"""
