####################################################
# makeResults.py
#
# Use this script to build the test.dat file. This
# file contains the vector representation of the
# entire corpus, with the docID removed and preceded
# by a zero.
#
# Usage:
#   python makeResults.py <vecrep file> <output file>
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
		line = tup1[2]
		tup2 = line.partition(" ")
		vecline = tup2[2]
		trainingOutput.write("0 " + vecline)
	
