import sys
import array


code = {10 : '\n',
		11 : ' ',
		12 : ':',
		13 : ','}

# this code value terminates the nibble stream
terminator = "14"

if __name__ == '__main__' :
	
	compressedFile = open(sys.argv[1], 'rb')
	postingFile = open(sys.argv[2], 'w')
		
	# read compressed file into a byte array
	in_bytes = compressedFile.read()
	compressedFile.close()
	
	# string to write out
	out_string = ""

	
	for b in in_bytes :
		
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
		
		if (nibble1 == terminator) :
			break;
		elif (nibble2 == terminator) :
			out_string += nibble1
		else :
			out_string += nibble1
			out_string += nibble2

			
	postingFile.write(out_string)
	postingFile.close()
	
	