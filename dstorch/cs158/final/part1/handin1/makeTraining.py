####################################################
# makeTraining.py
#
# Builds the complete 10,000 item training set
# from the provided file training.dat and the
# vecrep output.
#
# Usage:
#  python makeTraining.py <category> <vecrep file> <training set> <svmtrainingX.dat>
#
# Authors: David Storch (dstorch)
#          Matt Mahoney (mjmahone)
####################################################

import sys

if __name__ == '__main__' :
	
	cat = int(sys.argv[1])
	vecFile = open(sys.argv[2])
	trainingInput = open(sys.argv[3])
	trainingOutput = open(sys.argv[4], 'w')
	
	vecrep = dict()
	
	for line in vecFile :
		tup1 = line.partition(" ")
		docID = int(tup1[0])
		line = tup1[2]
		tup2 = line.partition(" ")
		vecrep[docID] = tup2[2]
	
	for line in trainingInput :
	  arr = line.split(" ")
	  docID = int(arr[0])
	  classif = arr[1]
	  trainVal = -1
	  if int(classif) == cat :
		trainVal = 1
	
	  trainingOutput.write(str(trainVal) + " " + vecrep[docID])
