########################################################
#			query.py
#
# Query a compressed binary file produced by
# compressor.py.
#
# Compression is done by using the differences between
# posting and position numbers, and then encoding each
# character using 4 bits instead of an entire byte
#
# Input/Output:
# 	Accepts indices, one per line, from the standard
#	input and returns decompressed postings lists,
#   one per line, to the standard output.
#
# Authors: David Storch (dstorch)
#		   Matt Mahoney (mjmahone)
#
# February 2011
#
########################################################

import sys
import array

########################################################
# The encoding used for non-numerical characters. For
# instance, the newline is encoded by the nibble 1010
# and a comma is encoded by 1101
########################################################
code = {10 : '\n',
		11 : ' ',
		12 : ':',
		13 : ','}

# this code value terminates a line
# if a newline is in the higher-order bits
eol = "14"
#########################################################


# The main decompression function.
#
# Input: An array of bytes read from the 
#		 compressed file
# Output: The string corresponding to the
#   decompressed byte array
def decompress(bytearray) :
	
	# string to write out
	out_string = ""

	for b in bytearray :
		
		# nibble1 is the higher-order nibble in the byte
		# nibble2 is the lower-order nibble
		nibble1 = ord(b) / (2**4)
		nibble2 = ord(b) % (2**4)
			
		if nibble1 in code :
			nibble1 = str(code[nibble1])
		else :
			nibble1 = str(nibble1)
		if nibble2 in code :
			nibble2 = str(code[nibble2])
		else :
			nibble2 = str(nibble2)
		
		if (nibble1 == eol) :
			break;
		elif (nibble2 == eol) :
			out_string += nibble1
		else :
			out_string += nibble1
			out_string += nibble2
			
	return str.strip(out_string)


# This function should be called immediately after decompress.
# It takes a newly decompressed postings list which is stored
# based on differences between docIDs and positional indices.
# This function does the addition necessary to restore the
# original indices.
#
# Calls postingAdder() as a helper.
#
# Input: a string corresponding to the postings list with
#   indices and docIDs stored by differences
# Output: a string that is the fully decompressed postings list
def lineAdder(line) :
	postings = line.split(' ')
	outputStringArr = []
	currentSum = 0
	for p in postings :
		fields = p.split(':')
		
		if len(fields) == 2 :
			outputStringArr.append(str(int(fields[0]) + currentSum) + ':' + postingAdder(fields[1]))
			currentSum += int(fields[0])
		elif len(fields) == 1 :
			outputStringArr.append(str(int(fields[0]) + currentSum))
			currentSum += int(fields[0])
		else :
			raise Error("Bad postings file")
		
	return (' '.join(outputStringArr))


# This function converts difference-based positional lists for each
# posting into the original positional list.
def postingAdder(p) :

	fields = p.split(',')
	lastPos = 0
	outputPositionArr = []
	
	for pos in fields :
		outputPositionArr.append(str(int(pos) + lastPos))
		lastPos += int(pos)
		
	return ','.join(outputPositionArr)


# Reads the first 8 bytes of the file in order
# to determine the size of the mini-index which
# immediately follows.
#
# Input: a filehandle for the compressed file
# Ouput: an integer, the number of bytes (not
#	counting the first 8 bytes) taken by the
#   mini-index
def getStartBytes(compressedFile) :
	byteNum = 0
	for i in range(1, 9) :
		byte = compressedFile.read(1)
		byteNum += ord(byte) << 8*(8 - i)
	return byteNum


##########################################
# MAIN
##########################################
if __name__ == '__main__' :
	
	compressedFile = open(sys.argv[1], 'rb')
	
	# get the bytes which encode how long the
	# mini-index is (the mini-index tells us where
	# in the byte array each of the postings lists live)s
	byteNum = getStartBytes(compressedFile)
	
	# read and decompress the mini-index
	startString = compressedFile.read(byteNum)
	startString = decompress(startString)
	startString = lineAdder(startString)
	
	byteNum += 8
	indexArray = startString.split(' ')
	
	receiveInput = True
	
	# main loop, receives from stdin
	while receiveInput :
		try:
			line = raw_input().strip()
		
			# make sure that input is valid
			if (line == "") :
				continue
		
			lineInt = int(line)
			bytesToJump = int(indexArray[lineInt]) + byteNum
			
			compressedFile.seek(bytesToJump, 0)
			lineString = compressedFile.read(int(indexArray[lineInt + 1]) - int(indexArray[lineInt]))
			lineString = decompress(lineString)
			lineString = lineAdder(lineString)
			print str.strip(lineString)
		
		# catch error from invalid integer
		except ValueError:
			print "" # just a newline
		
		# catch error from out of bounds exception
		except IndexError:
			print "" # just a newline
		
		except EOFError:
			receiveInput = False
			
			
			
	
	
	
	