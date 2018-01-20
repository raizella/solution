import sys

if __name__ == '__main__' :
	
	f1 = open(sys.argv[1])
	f2 = open(sys.argv[2])
	
	f1Dict = dict()
	total = 0
	numSame = 0
	
	for line in f1:
		arg = line.split(" ")
		docID = int(arg[0])
		classified = int(arg[1])
		f1Dict[docID] = classified
		
	for line in f2:
		arg = line.split(" ")
		docID = int(arg[0])
		classified = int(arg[1])
		if docID in f1Dict :
			f1result = f1Dict[docID]
			total += 1
			if f1result == classified :
				numSame += 1
			
			
				
	print "total: " + str(total)
	print "num same: " + str(numSame)
	print "error: " + str(float(total-numSame)/float(total))
	#print "percentage: " + str(float(numSame)/total)