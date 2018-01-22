####################################################
# convertToTest.py
#
# Given an svmtrainingX.dat file, converts it to
# a "test file" that can be used by svm_classify.
# This program simply replaces the classification
# at the beginning of the training set with
# a 0 (instead of -1 or +1).
#
# Authors: David Storch (dstorch)
#          Matt Mahoney (mjmahone)
####################################################


import sys

if __name__ == '__main__' :
	
	vecFile = open(sys.argv[1])
	trainingOutput = open(sys.argv[2], 'w')
	
	vecrep = dict()
	
	for line in vecFile :
		tup1 = line.partition(" ")
		vecline = tup1[2]
		trainingOutput.write("0 " + vecline)
	