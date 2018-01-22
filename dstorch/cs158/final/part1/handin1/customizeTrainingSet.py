####################################################
# customizeTrainingSets.py
#
# This script is used to analyze the classification
# results when reapplied to the training data.
# Prints out a number of useful classification
# stats.
#
# Takes in the training file, the corresponding
# prediction file, and the output file to which
# we write the updated training set.
#
# Usage:
#   python makeResults.py <svmtrainingX.dat> <predictionX.dat> <class number>
#
# Authors: David Storch (dstorch)
#          Matt Mahoney (mjmahone)
####################################################

import sys

trainingFile = open(sys.argv[1])
predictions = open(sys.argv[2])
outfile = open(sys.argv[3], 'w')

booleans = []
for line in predictions :
	val = float(line)
	if val < 0 and val > -1.05 :
		booleans.append(True)
	else :
		booleans.append(False)
		
for i, line in enumerate(trainingFile) :
	tup = line.partition(" ")
	classif = int(tup[0])
	if (not booleans[i]) or classif == 1 :
		outfile.write(line)
		

