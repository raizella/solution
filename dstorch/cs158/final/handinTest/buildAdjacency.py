##################################################
#
# Authors:
#   David Storch (dstorch)
#   Matthew Mahoney (mjmahone)
#   April 2011
##################################################

import sys
import re
import math

from parseCollection import XMLParser


if __name__ == '__main__' :
	
	# filehandles
	collection = open(sys.argv[1])
	outfile = open(sys.argv[2], 'w')

	# extract docID, title, and text from the XML
	xmlparse = XMLParser(collection)
	parsedPages = xmlparse.parseCollection()
	
	# the number of documents
	N = float(len(parsedPages))
	
	title2id = dict()
	adjacency = []
	
	# set up map from title to docID
	for p in parsedPages :
		title2id[p._title] = p._id
		
	# build the adjacency matrix
	for p in parsedPages :

		adjacencyList = []
		
		matches = re.findall("\[\[[^\[\]]*\]\]", (p._pzone + "\n" + p._text))
		 
		for match in matches :
			match = match[2:-2]
			
			arr = match.split("|")
			match = arr[0]
			arr = match.split("#")
			match = arr[0]
			
			if match in title2id :
				if not title2id[match] in adjacencyList :
					adjacencyList.append(title2id[match])
				
		adjacency.append(adjacencyList)
				
	# write out to the file
	for i, adjList in enumerate(adjacency) :
		if len(adjList) == 0 :
			continue
		degree = str(1.0/float(len(adjList)))
		for j in adjList :
			outfile.write(str(i+1) + " " + str(j+1) + " " + degree + "\n")
	

