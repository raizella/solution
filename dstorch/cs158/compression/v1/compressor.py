import sys
import array

code = {'\n' : 10,
		' '  : 11,
		':'	 : 12,
		','	 : 13}

# this code value terminates the nibble stream
terminator = 14
	

if __name__ == '__main__' :
	
	postingFile = open(sys.argv[1], 'rb')
	compressedFile = open(sys.argv[2], 'wb')
	
	# read posting file into a byte array
	in_bytes = postingFile.read()
	postingFile.close()
	
	# byte array to write out
	out_bytes = array.array('B')
	
	for i in range(0, len(in_bytes), 2) :
		
		if i == len(in_bytes) - 1 :
			byte = in_bytes[i]
			if byte in code :
				byte = int(code[byte])
			else :
				byte = int(byte)
			outb = (byte << 4) + terminator
			out_bytes.append(outb)
		
		else :
			
			byte1 = in_bytes[i]
			byte2 = in_bytes[i+1]
			
			if byte1 in code :
				byte1 = int(code[byte1])
			else :
				byte1 = int(byte1)
			if byte2 in code :
				byte2 = int(code[byte2])
			else :
				byte2 = int(byte2)					
	
			output_byte = (byte1 << 4) + byte2
			
			out_bytes.append(int(output_byte))
		
	
	
	# add an extra termination byte
	last_byte = (terminator << 4) + terminator
	out_bytes.append(last_byte);
	
	out_bytes.tofile(compressedFile)
	compressedFile.close()