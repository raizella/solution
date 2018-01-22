######################################################
# evaluateTestQueries.py -
#   Compares the results from a simple tf-idf based
#   search engine to a more nuanced search engine making
#   use of PageRank, zones, and various heuristics.
#
# Outputs the docIDs which both versions of the search
# engine return, along with the number of shared docIDs.
# On the last line, prints the average number of shared
# docIDs.
#
# Author:
#  David Storch
#  login - dstorch
#  May 2011
#
######################################################

import sys

expected = open(sys.argv[1])
results = open(sys.argv[2])

sizeList = []

for i, exp in enumerate(expected) :
	
	exp = exp.strip()
	res = results.readline().strip()
	resArr = res.split(" ")
	expArr = exp.split(" ")
	
	resSet = set()
	expSet = set()
	
	for docID in resArr :
		if docID != "" :
			resSet.add(int(docID))
		
	for docID in expArr :
		if docID != "" :
			expSet.add(int(docID))
		
	intersect = resSet.intersection(expSet)
	
	sys.stdout.write("num:"+str(len(intersect))+" ")
	
	sizeList.append(len(intersect))
	
	for docID in intersect :
		sys.stdout.write(str(docID)+" ")
		
	sys.stdout.write("\n")

sys.stdout.write(str(float(sum(sizeList)) / float(len(sizeList))))

