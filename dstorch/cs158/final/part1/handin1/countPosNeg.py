####################################################
# countPosNeg.py
#
# Counts the number of positive and negative
# training examples in one of the training sets,
# that is, one of the files trainingX.dat.
#
# Authors: David Storch (dstorch)
#          Matt Mahoney (mjmahone)
####################################################

import sys

trainingFile = open(sys.argv[1])
classNum = sys.argv[2]

size = 0
positive = 0
negative = 0

for line in trainingFile :
	tup = line.partition(" ")
	classif = int(tup[0])
	
	size += 1
	
	if classif == 1 :
		positive += 1
	elif classif == -1 :
		negative += 1

print "Class: ", classNum
print "---------"
print "Size: ", size
print "Positive: ", positive
print "Negative: ", negative
print ""
