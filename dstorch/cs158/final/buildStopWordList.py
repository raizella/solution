
import sys
import re
import operator

from parseCollection import XMLParser

if __name__ == "__main__" :

	collection = open(sys.argv[1])
	stopWordsList = open(sys.argv[2], 'w')
	
	# extract docID, title, and text from the XML
	xmlparse = XMLParser(collection)
	parsedPages = xmlparse.parseCollection()
	
	# we will compute the document frequency
	# and the collection frequency
	docFreq = dict()
	collectionFreq = dict()
	
	N = len(parsedPages)
	
	for p in parsedPages :
		
		docID = p._id
		text = p._pzone + "\n" + p._text
		
		# tokenize
		text = text.strip()
		listOfTerms = re.split('[^a-zA-Z0-9]+', text.lower())
		
		docTermSet = set()
		
		for term in listOfTerms :
			
			if not term in collectionFreq :
				collectionFreq[term] = 1
			else :
				collectionFreq[term] += 1
			
			docTermSet.add(term)
			
		for term in docTermSet :
			
			if not term in docFreq :
				docFreq[term] = 1
			else :
				docFreq[term] += 1
	 
	# get a list of terms that appear in more than 99% of the documents
	sortedTerms = sorted(docFreq.iteritems(), key=operator.itemgetter(1))
	
	for term, freq in sortedTerms :
		
		if (float(freq) / float(N)) > 0.75 :
			if term != "" :
				stopWordsList.write(term + "\n")
				
	# look at the distribution of document frequency
	bins = dict()
	bins[0] = 0
	bins[1] = 0
	bins[2] = 0
	bins[3] = 0
	bins[4] = 0
	bins[5] = 0
	bins[6] = 0
	
	###############################################
	# MAKE A HISTOGRAM -- for analyzing doc freq
	###############################################
	
	for term in docFreq :
		
		freq = docFreq[term]
		
		# make the histogram
		if freq >= 0 and freq < 10 :
			bins[0] += 1
		if freq >= 10 and freq < 100 :
			bins[1] += 1
		if freq >= 100 and freq < 1000 :
			bins[2] += 1
		if freq >= 1000 and freq < 10000 :
			bins[3] += 1
		if freq >= 1000 :
			bins[4] += 1
			
	for i in range(0, 5) :
		print "In bin ", i, ": ", bins[i]
			

