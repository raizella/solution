import sys
import math

# read in the vecrep file, and 
# create a dictionary of docID, (dictionary of featureID, frequency)
def readVecRep(vecRep) :
	bigDict = dict()
	for line in vecRep :
		
		littleDict = dict()
		
		fields = line.split(" ")
		docID = int(fields[0])
		fields = fields[2:]
		
		for pair in fields :
			pair = pair.strip()
			pair = pair.split(":")
			littleDict[int(pair[0])] = int(pair[1])
			
		bigDict[docID] = littleDict
		
	return bigDict

def printQ1(vecrep):
	
	totalIDs = 0.0
	totalFeatures = 0.0
	featureDict = dict()
	
	for i in vecrep:
		totalIDs += 1.0
		totalFeatures += len(vecrep[i])
		for f in vecrep[i] :
			if f in featureDict :
				featureDict[f] += 1
			else :
				featureDict[f] = 1
	
	#for f in sorted(featureDict.keys()) :
		#print str(f) + "," + str(featureDict[f])
	
	print totalIDs
	print totalFeatures
	print totalFeatures/totalIDs
	return featureDict
	
	
if __name__ == '__main__' :
	
	vecrep1 = open(sys.argv[1])
	outfile = open(sys.argv[2], 'w')
	
	vecDict1 = readVecRep(vecrep1)
	
	featureDict = printQ1(vecDict1)
	
	frequencyDict = dict()
	
	for f in featureDict :
		freq = featureDict[f]
		if freq in frequencyDict :
			frequencyDict[freq] += 1
		else :
			frequencyDict[freq] = 1
	
	for n in sorted(frequencyDict.keys()) :
		l = math.log(frequencyDict[n])
		outfile.write(str(n) + "," + str(frequencyDict[n]) + ',' + str(l) + '\n')
	