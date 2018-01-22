####################################################
# compareResults.py
#
# This script is used to analyze the classification
# results when reapplied to the training data.
# Prints out a number of useful classification
# stats.
#
# Takes in the training file, the corresponding
# prediction file, and the number of the class for
# these two files.
#
# Usage:
#   python makeResults.py <svmtrainingX.dat> <predictionX.dat> <class number>
#
# Authors: David Storch (dstorch)
#          Matt Mahoney (mjmahone)
####################################################

import sys

if __name__ == '__main__' :
	
	svmTrain = open(sys.argv[1])
	prediction = open(sys.argv[2])
	classNum = sys.argv[3]
	
	epsilon = 0.1
	
	classification = dict()
	
	
	for i, line in enumerate(svmTrain) :
		tup = line.partition(" ")
		val = int(tup[0])
		classification[i] = val
	
	everyTime = 0
	classifiedRight = 0
	classifiedWrong = 0
	shouldHaveBeenClassified = 0
	wasntisnt = 0
	
	for i, line in enumerate(prediction) :
		everyTime += 1
		val = float(line)
		orig = classification[i]
		if val >= epsilon :
			if orig == 1 :
				classifiedRight += 1
			else :
				classifiedWrong += 1
		else :
			if orig == 1 :
				shouldHaveBeenClassified += 1
			else :
				wasntisnt += 1
	
	print "Class: ", classNum
	print "--------"
	print "Total classifications: ", everyTime
	print "Number Classified Correctly: ", classifiedRight + wasntisnt
	print "Number Classified Incorrectly: ", classifiedWrong + shouldHaveBeenClassified
	print "Was classified, should have been: ", classifiedRight
	print "Was classified, shouldn't have been: ", classifiedWrong
	print "Should have been classified, wasn't: ", shouldHaveBeenClassified
	print "Shouldn't have been classified, wasn't: ", wasntisnt
	print "Precision: ", float(classifiedRight) / float(classifiedRight + classifiedWrong) * 100
	print "Recall: ", float(classifiedRight) / float(classifiedRight + shouldHaveBeenClassified) * 100
	print ""
		