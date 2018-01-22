########################################################
#			compressor.py
#
# Write a compressed version of a positional or non-
# positional index file.
#
# Compression is done by using the differences between
# posting and position numbers, and then encoding each
# character using 4 bits instead of an entire byte.
#
# Arguments:
#   arg1 - the name of the postings file
#   arg2 - the name of the compressed outfile to be generated;
#		   the output is a nibble-based binary encoding
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
code = {'\n' : 10,
		' '  : 11,
		':'	 : 12,
		','	 : 13}

# this code value terminates a line
# if a newline is in the higher-order bits
eol = 14

# Global variable keeping track of the current size of
# the byte array to write out.
currentNumBytes = 0
#########################################################



# Takes in a line (a string), and returns a smaller string.
# The smaller string is obtained by storing differences
# instead of the original postings and positional numbers.
#
# Calls postingSubstractor() as a helper.
#
# Input: a string, the original postings list
# Output: a string, the difference-based postings list
def lineSubtractor(line) :
	postings = line.split(' ')
	outputStringArr = []
	lastDocID = 0
	for p in postings :
		fields = p.split(':')
		
		if len(fields) == 2 :
			outputStringArr.append(str(int(fields[0]) - lastDocID) + ':' + postingSubtractor(fields[1]))
			lastDocID = int(fields[0])
		elif len(fields) == 1 :
			outputStringArr.append(str(int(fields[0]) - lastDocID))
			lastDocID = int(fields[0])
		else :
			raise Error("Bad postings file")
		
	return (' '.join(outputStringArr))


# Takes in a position list (a string) and returns
# a string representing the same list, except storing
# differences instead of the original position numbers.
#
# Input: a string, the original position list
# Output: a string, the difference-based postings list
def postingSubtractor(p) :

	fields = p.split(',')
	lastPos = 0
	outputPositionArr = []
	
	for pos in fields :
		outputPositionArr.append(str(int(pos) - lastPos))
		lastPos = int(pos)
		
	return ','.join(outputPositionArr)




# Converts the integer num into a byte array
# representation.
#
# Input:
#  num - the integer to store as a byte array
#  bytes - an integer, the number of bytes to
#	    use to store num
#
# Does not protect against overflow---i.e.,
# will not work if num cannot be stored using
# the specified number of bytes
def getByteArray(num, bytes) :
	bytearr = []
	for i in range(0, bytes) :
		bytearr.append(num % 256)
		num = num / 256
	return bytearr





# The main compression function
#
# Input:
#	line - a string, the line to compress
#	out_bytes - the binary array which will
#	  	be written as the compressed file. This
#	  	method appends the compressed version of
#     	the input line to the out_bytes array.
#	lineBeginnings - the array which will store
#		the byte number in the compressed file
#		at which this line starts
def compress(line, out_bytes, lineBeginnings) :
	# do subtraction of postings lists
	line = lineSubtractor(line)
	
	numOutputBytes = 0
	
	# go through the input line in groups
	# of 2 bytes
	for i in range(0, len(line), 2) :
		
		# case: line[i] is the last byte
		if i == len(line)-1 :
			byte = line[i]
			if byte in code :
				byte = int(code[byte])
			else :
				byte = int(byte)
			outb = (byte << 4) + eol
			numOutputBytes += 1
			out_bytes.append(outb)
		
		# case: line[i] is not the last byte
		else :
			
			byte1 = line[i]
			byte2 = line[i+1]
			
			if byte1 in code :
				byte1 = int(code[byte1])
			else :
				byte1 = int(byte1)
			if byte2 in code :
				byte2 = int(code[byte2])
			else :
				byte2 = int(byte2)					
	
			output_byte = (byte1 << 4) + byte2
			
			numOutputBytes += 1
			out_bytes.append(int(output_byte))
	
	# record the byte number at which this line begins
	lastLineBeginning = lineBeginnings[-1]
	lineBeginnings.append(lastLineBeginning + numOutputBytes)



##########################################
# MAIN
##########################################
if __name__ == '__main__' :
	
	postingFile = open(sys.argv[1], 'r')
	compressedFile = open(sys.argv[2], 'wb')
	
	# byte array to write out
	out_bytes = array.array('B')
	
	# keep track of the byte at which each line begins
	lineBeginnings = [0]
	
	# do the compression for each line
	for line in postingFile :
		compress(line, out_bytes, lineBeginnings)

	# compress the index that stores the beginning position of each line
	for index, num in enumerate(lineBeginnings) :
		lineBeginnings[index] = str(lineBeginnings[index])
	lineBeginningsStr = ' '.join(lineBeginnings)
	index_bytes = array.array('B')
	
	beginningsCompressedLength = [0]
	compress(lineBeginningsStr, index_bytes, beginningsCompressedLength)
	
	# use 8 bytes to store the length of the index
	bytearr = getByteArray(beginningsCompressedLength[1], 8)
	
	# actually produce the byte array
	beginning_bytes = array.array('B')
	for b in bytearr :
		beginning_bytes.insert(0, b)
	
	# write binary arrays to the outfile
	# in the proper sequence
	beginning_bytes.tofile(compressedFile)
	index_bytes.tofile(compressedFile)
	out_bytes.tofile(compressedFile)
	
	# close the filehandles
	compressedFile.close()
	postingFile.close()
	
	