##################################################
#			createIndex.py
#
# Index a subset of Wikipedia, and write the
# resulting inverted index to a file. This
# index can then be queried by queryIndex.py.
#
# Arguments
#   arg1 - xml text file containing the original collection
#   arg2 - index file to output
#
# Author:
#   David Storch (dstorch)
#   May 2011
##################################################

import sys
import PorterStemmer
import re
import math
import os
from Weights import WeightHolder
from parseCollection import XMLParser

##################################################
# GLOBALS
##################################################

stopWordSet = set()

pstemmer = PorterStemmer.PorterStemmer()

# the number of pages in the collection
N = -1

# the number of words that the bottom sections
# of characters the bottom sections of the wiki
# page must exceed in order to not be considered a stub
minimumStubChars = 1000

weights = WeightHolder()

##################################################


##############################################################################################
########### CONSTRUCTING THE INVERTED INDEX   -- HELPER FUNCTIONS         ####################
##############################################################################################

def tokenize(text) :
	
		#split the terms into a list
		listOfTerms = re.split('[^a-z0-9]+', text)
		
		# remove first and last list elements if they are ''
		if len(listOfTerms) > 0 :
			if listOfTerms[0] == '' :
				listOfTerms.pop(0)
				
		if len(listOfTerms) > 0 :
			if listOfTerms[len(listOfTerms) - 1] == '' :
				listOfTerms.pop()
			
		return listOfTerms

def buildIndexDictionary(listOfTerms, bigDict) :
		
	# build the inverted index
	index = 0
	for term in listOfTerms :
		if term in stopWordSet :
			continue
		term = PorterStemmer.stemWord(pstemmer, term)
		if term in bigDict :
			littleDict = bigDict[term]
			if docID in littleDict :
				littleDict[docID].append(index)
			else :
				littleDict[docID] = [index]
		else :
			bigDict[term] = dict({docID : [index]})
		index += 1
	
	return bigDict
		
def computeWeights(bigDict, normalizationDict) :
	
	# calculate weights
	for term in bigDict :
		idf = math.log(N / len(bigDict[term].keys()))
		
		littleDict = bigDict[term]
		for docID in littleDict :
			normalizationDict[docID] += len(littleDict[docID])**2
		
		idfDict[term] = idf
	
	# take the square roots to get the final Euclidian normalization factors
	for docID in normalizationDict :
		normalizationDict[docID] = math.sqrt(normalizationDict[docID])
		
	return bigDict, normalizationDict
	
def writeIndex(indexFile, bigDict, normalizationDict, positionMap) :
	
	# NOTE: reserve 21 bytes for the length of the dictionary
	# (last character is a newline)
	
	# determine byte-positions, not taking length of header into account
	currentBytes = 0
	for term in bigDict:
		positionMap[term] = currentBytes
		littleDict = bigDict[term]
		currentBytes += len(str(idfDict[term]))
		for docID in littleDict :
			currentBytes += len(":" + str(docID))
			for pos in littleDict[docID] :
				currentBytes += len(" " + str(pos))
		currentBytes += 1
	
	# determine the length of the header dictionary
	dictionaryLength = 0
	for term in positionMap :
		dictionaryLength += len(term + " " + str(positionMap[term]) + "\n")
		
	# determine the length of the normalization dictionary
	normLength = 0
	for docID in normalizationDict :
		normLength += len(str(docID) + " " + str(normalizationDict[docID]) + "\n")
	
	# find length of the headers
	dictionaryLengthStr = str(dictionaryLength)
	normLengthStr = str(normLength)
	
	# write dictionary length to the beginning of the file
	for i in range(0, 20 - len(dictionaryLengthStr)) :
		indexFile.write('0')
	indexFile.write(dictionaryLengthStr + "\n")
	
	# write the length of the normalization info to the beginning
	for i in range(0, 20 - len(normLengthStr)) :
		indexFile.write('0')
	indexFile.write(normLengthStr + "\n")
	
	# write the dictionary
	for term in positionMap :
		position = positionMap[term]
		indexFile.write(term + " " + str(position) + "\n")
		
	# write the normalization info
	for docID in normalizationDict :
		indexFile.write(str(docID) + " " + str(normalizationDict[docID]) + "\n")
	
	# write the inverted index
	for term in bigDict:
		littleDict = bigDict[term]
		indexFile.write(str(idfDict[term]))
		for docID in littleDict :
			indexFile.write(":" + str(docID))
			for pos in littleDict[docID] :
				indexFile.write(" " + str(pos))
		indexFile.write("\n")

		 
##############################################################################################
##############################################################################################
##############################################################################################

if __name__ == '__main__' :
	
	# filehandles
	collection = open(sys.argv[1])
	indexFile = open(sys.argv[2], 'w')
	stopWords = open(sys.argv[3])
	titleIndex = open(sys.argv[4], 'w')
	pzoneFile = open(sys.argv[5], "w")
	
	# create a set of stop words from the stopWords infile
	# assuming that there is one word per line
	for line in stopWords:
		stopWordSet.add(str.strip(line))
	
	# extract docID, title, and text from the XML
	xmlparse = XMLParser(collection)
	parsedPages = xmlparse.parseCollection()
	
	# maps from terms to smaller dictionaries
	bigDict = dict()
	zoneDict = dict()
	
	# maps from terms to idf
	idfDict = dict()
	zoneIdf = dict()
	
	# maps from docID to euclidian normalization factor
	normalizationDict = dict()
	zoneNormalization = dict()
	
	# the number of documents
	N = float(len(parsedPages))
	
	# set up the inverted index
	for p in parsedPages :
		
		docID = p._id
		
		# write the title index
		stub1 = 0
		stub2 = 0
		if len(p._pzone) < weights.getMinimumStubChars() :
			stub1 = 1
		if len(p._text) < weights.getMinimumStubChars() :
			stub2 = 1
		titleIndex.write(str(p._id) +"\t"+str(stub1)+"\t"+str(stub2)+"\t"+p._title+"\n")

		# tokenize different zones
		listOfTerms = tokenize((p._text).lower())
		zoneTerms = tokenize((p._pzone).lower())
		
		# build the dictionaries
		bigDict = buildIndexDictionary(listOfTerms, bigDict)
		zoneDict = buildIndexDictionary(zoneTerms, zoneDict)
		
		# initialize all normalization factors to 0
		normalizationDict[docID] = 0.0
		zoneNormalization[docID] = 0.0
		
	# pre-compute information for tf-idf weighting
	bigDict, normalizationDict = computeWeights(bigDict, normalizationDict)
	zoneDict, zoneNormalization = computeWeights(zoneDict, zoneNormalization)
	
	# a map from each term to absolute position
	# in the file---we want to be able to seek
	# to the correct position in the postings list
	positionMap = dict()
	zonePosMap = dict()
	
	# write out the index files
	writeIndex(indexFile, bigDict, normalizationDict, positionMap)
	writeIndex(pzoneFile, zoneDict, zoneNormalization, zonePosMap)

	
