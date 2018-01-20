##############################################
# features.py
# Determine a good set of features, based on
# the training data.
###############################################

import re
import sys
import PorterStemmer
from operator import itemgetter

########################
# SET PARAMETERS HERE
########################
percentCutoff = 0.3
frequencyCutoff = 10


def realFind(line, searchString) :
	index = str.find(line, searchString)
	if index != -1 :
		index += len( searchString)
	return index

class XMLParser(object):
	def __init__(self, toParse) :
		self._toParse = toParse
		
	#returns list of parsed pages
	def parseCollection(self) :
		self._toParse
		while not self._toParse.closed :
			#need to catch EOF error
			line = self._toParse.readline()
			openIndex = realFind(line, "<collection>")
			if openIndex != -1 :
				return self.parsePages(line[openIndex:])
			
			
	def parsePages(self, restOfLine) :
		pageList = []
		
		line = restOfLine
		
		while str.find(line, "</collection>") == -1 :
			openIndex = realFind(line, "<page>")
			if openIndex != -1 :
				page = ParsedPage(self._toParse)
				page.parse(line[openIndex:])
				pageList.append(page)
		
			line = self._toParse.readline()
		
		return pageList

##########################################################################

# A ParsedPage object packages the id number, title,
# and text contained within each page tag
class ParsedPage(object) :
	def __init__(self, toParse) :
		self._toParse = toParse
		self._id = -1
		self._title = ""
		self._text = ""
		
	# the main parsing method of this object
	def parse(self, restOfLine) :
		line = restOfLine
		
		while str.find(line, "</page>") == -1 :
			
			idIndex = realFind(line, "<id>")
			titleIndex = realFind(line, "<title>")
			textIndex = realFind(line, "<text>")
			
			if idIndex != -1 :
				line = self.idParse(line[idIndex:])
			
			if titleIndex != -1:
				line = self.titleParse(line[titleIndex:])
			
			if textIndex != -1:
				line = self.textParse(line[textIndex:])
		
			line = self._toParse.readline()
	
	
	def idParse(self, restOfLine) :
		line = restOfLine
		
		pageID = ""
		
		beginIndex = str.find(line, "</id>")
		
		while beginIndex == -1 :
			pageID += line
			line = self._toParse.readline()
			beginIndex = str.find(line, "</id>")
			
			
		pageID += line[:beginIndex]
			
		# once out of the loop, we have found the id
		self._id = int(pageID)
		
		# return the text after the closing tag
		return line[beginIndex:]
		
	def titleParse(self, restOfLine) :
		line = restOfLine
		
		pageTitle = ""
		
		beginIndex = str.find(line, "</title>")
		
		while beginIndex == -1 :
			pageTitle += line
			line = self._toParse.readline()
			beginIndex = str.find(line, "</title>")
			
			
		pageTitle += line[:beginIndex]
			
		# once out of the loop, we have found the id
		self._title = pageTitle
		
		# return the text after the closing tag
		return line[beginIndex:]
	
	def textParse(self, restOfLine) :
		line = restOfLine
		
		pageText = ""
		
		beginIndex = str.find(line, "</text>")
		
		while beginIndex == -1 :
			pageText += line
			line = self._toParse.readline()
			beginIndex = str.find(line, "</text>")
			
			
		pageText += line[:beginIndex]
			
		# once out of the loop, we have found the id
		self._text = pageText
		
		# return the text after the closing tag
		return line[beginIndex:]
	
	def page_print(self) :
		print(self._id)
		print(self._title)
		print(self._text)
		 
	
	
##############################################################################################

# readTrainingData
# arg - a filehandle for the training data set
# 
# Returns a dictionary where each class number maps to
# a list of docIDs belonging to that classification.
def readTrainingData(training) :
	trainingDict = dict()
	testData = dict()
	for line in training :
		fields = line.split(" ")
		docID = int(fields[0])
		classification = int(fields[1])
		
		testData[docID] = int(classification)
		
		if classification in trainingDict :
			trainingDict[classification].append(docID)
		else :
			trainingDict[classification] = [docID]
	
	return trainingDict, testData

def printOutputStats(bigDict, totalDict, featuresADV) :
	outSet = set()
	classes = sorted(bigDict.keys())
	ratioDict = dict()
	for classif in classes :
		print "CLASS ", classif
		print "-----"
		
		littleDict = bigDict[classif]
		ratioDict[classif] = dict()
		for term in littleDict :
			ratio = float(littleDict[term]) / float(totalDict[term])
			ratioDict[classif][term] = ratio
		
		for term, ratio in sorted(ratioDict[classif].items(), key=itemgetter(1), reverse=True) :
			if ratio >= percentCutoff and bigDict[classif][term] >= frequencyCutoff :
				print term, ratio, bigDict[classif][term]
				outSet.add(term)
	
	for term in outSet :
		featuresADV.write(term+"\n")
		

if __name__ == '__main__' :
	
	stopWords = open(sys.argv[1])
	collection = open(sys.argv[2])
	training = open(sys.argv[3])
	featuresADV = open(sys.argv[4], 'w')
	
	pstemmer = PorterStemmer.PorterStemmer()
	
	# create a set of stop words from the stopWords infile
	# assuming that there is one word per line
	stopWordSet = set()
	for line in stopWords:
		stopWordSet.add(str.strip(line))
		
	trainingDict, testData = readTrainingData(training)
	bigDict = dict()
	totalDict = dict()
		
	# extract docID, title, and text from the XML
	xmlparse = XMLParser(collection)
	parsedPages = xmlparse.parseCollection()
		
	for p in parsedPages :
		docID = int(p._id)
		
		if not docID in testData :
			continue
		
		classif = testData[docID]
		if not classif in bigDict :
			bigDict[classif] = dict()
		
		#split the terms into a list to walk through
		listOfTerms = re.split('[^a-z0-9]+', (p._title + "\n" + p._text).lower())
		if listOfTerms[0] == '' :
			listOfTerms.pop(0)
		if listOfTerms[len(listOfTerms) - 1] == '' :
			listOfTerms.pop()
			
		# iterate over each term in the page
		for term in listOfTerms :
			if not term in stopWordSet :
				term = PorterStemmer.stemWord(pstemmer, term)
				
				if not term in bigDict[classif] :
					bigDict[classif][term] = 1
				else :
					bigDict[classif][term] += 1
				
				if not term in totalDict :
					totalDict[term] = 1
				else :
					totalDict[term] += 1
				
				
	printOutputStats(bigDict, totalDict, featuresADV)
				
	
	