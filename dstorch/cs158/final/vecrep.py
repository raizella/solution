import sys
import PorterStemmer
import re

from parseCollection import XMLParser


if __name__ == '__main__' :
	stopWords = open(sys.argv[1])
	collection = open(sys.argv[2])
	features = open(sys.argv[3])
	vecRep = open(sys.argv[4], 'w')
	
	pstemmer = PorterStemmer.PorterStemmer()
	
	# create a set of stop words from the stopWords infile
	# assuming that there is one word per line
	stopWordSet = set()
	for line in stopWords:
		stopWordSet.add(str.strip(line))
	
	# create a set of the features, as well as a dictionary matching <featureNum> to a word
	featureDict = dict()
	i = 0
	for line in features:
		#features are already stemmed
		f = str.strip(line)
		featureDict[f] = i
		i += 1
	
	# extract docID, title, and text from the XML
	xmlparse = XMLParser(collection)
	parsedPages = xmlparse.parseCollection()
	
	# maps from docID to feature vector
	bigDict = dict()
	
	# maps from doc ID to the euclidian norm of
	# the vector squared
	sumOfSquares = dict()
	
	# set up the inverted index
	for p in parsedPages :
		
		docID = p._id
		vector = dict()
		bigDict[docID] = vector
		
		#split the terms into a list to walk through
		listOfTerms = re.split('[^a-z0-9]+', (p._title+"\n"+p._pzone+"\n"+p._text).lower())
		if listOfTerms[0] == '' :
			listOfTerms.pop(0)
		if listOfTerms[len(listOfTerms) - 1] == '' :
			listOfTerms.pop()
		
		for term in listOfTerms :
			term = PorterStemmer.stemWord(pstemmer, term)
			
			if term in featureDict :
				if term in vector :
					vector[term] += 1
				else :
					vector[term] = 1
					
	for docID in bigDict :
		
		vector = bigDict[docID]
		sum = 0
		
		for term in vector :
			sum += vector[term] * vector[term]
			
		sumOfSquares[docID] = sum
		
	sortIDs = sorted(bigDict.keys())
	
	for docID in sortIDs :
		vecRep.write(str(docID) + " " + str(sumOfSquares[docID]))
		vector = bigDict[docID]
		
		toWriteDict = dict()
		for term in vector :
			toWriteDict[featureDict[term]] = vector[term]
		
		for t in sorted(toWriteDict.keys()):
			vecRep.write(" " + str(t) + ":" + str(toWriteDict[t]))
		vecRep.write("\n")
			