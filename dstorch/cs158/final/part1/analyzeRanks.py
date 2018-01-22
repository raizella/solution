import sys
import operator

##################################
# Sort the page rank results
#

file = open("pageRank.dat")

ranks = dict()
for i, line in enumerate(file) :
	ranks[i] = float(line)

sortedRanks = sorted(ranks.iteritems(), key=operator.itemgetter(1))

for docID, rank in sortedRanks :
	print docID, rank

