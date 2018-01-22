##################################################
#			queryIndex.py
#
# Queries an inverted index produced by createIndex.py.
# Uses a vector space ranking model to return the doctIDs
# of the top K hits.
#
# Arguments
#	arg0 - indexFile, the main index to read from
#	arg1 - zoneFile, the file indexing just the main
#		 section of each wikipage
#	arg2 - stopWords, gives the stop words one per line
#	arg3 - pageRankFile, gives the page rank, in order of docIDs,
#		one per line
#	arg4 - gives <docID> <stub?> <title>
#		A wikipage is considered a stub if the text following
#		the top section is less than 1000 characters long
#
# Author:
#   David Storch (dstorch)
#   May 2011
##################################################

import PorterStemmer
import re
import sys
import math
import heapq
from bool_parser import bool_expr_ast
from BTrees.OOBTree import OOBTree
from Weights import WeightHolder


##################################################
# GLOBAL VARIABLES
##################################################

# global constant---number of docs to retrieve
K = 10

# global stemmer
pstemmer = PorterStemmer.PorterStemmer()

# global set of stopWords
stopWordSet = set()

# global dictionary of titles (stemmed and stop-worded)
titles = dict()
rawTitles = dict()

# global dictionaries determining whether or not
# a file is a stub
stubsHeader = dict()
stubsBody = dict()

# keep a dictionary with the Naive Multinomial
# Bayes classification of each document
mnbClassif = dict()

# the total number of documents in each class,
# according to Multinomial Naive Bayes
totalInClass = dict()

##################################################


##################################################
#########     PREPROCESSING        ###############
##################################################


# input: a string s
# output: s with its characters rotated once to the
#	left. For example, if s="food" then rotateLeft(s)
#	will return "oodf"
def rotateLeft(s) :
	return s[1:] + s[:1]

# Adds all rotations of a term to the permuterm
# input:
#	1. a term s
#   2. the number of the byte at which the corresponding
#	   postings list begins
def makePermuterms(btree, s, num) :
	s = s + '$'
	while(s[0] != '$'):
		btree[s] = num
		s = rotateLeft(s)
	btree[s] = num

# Given an index file, reads in the header information
# in order to construct the btree and the normalization
# dictionary in memory.
#
# Input:
#	1. indexFile, a file handle for the inverted index
def buildDictionary(indexFile, btree, normDict) :
	dictionaryBytes = long(indexFile.readline())
	normBytes = long(indexFile.readline())
	
	# build the permuterm btree
	dictionaryString = indexFile.read(dictionaryBytes)
	dictionaryList = dictionaryString.split('\n')
	for line in dictionaryList :
		if len(line) > 1 :
			fields = line.split(' ')
			makePermuterms(btree, fields[0], long(fields[1]) + 42 + dictionaryBytes + normBytes)

			
	# build the normalization dict
	normString = indexFile.read(normBytes)
	normList = normString.split('\n')
	for line in normList :
		if len(line) > 1 :
			fields = line.split(' ')
			normDict[int(fields[0])] = float(fields[1])

# input: the raw query string
# output: a processed query string
#	with stop words removed, lowercasing done,
#	stemming done
def preProcessString(s) :
	isWrapped = isWrappedInQuotes(s)
	s = s.strip()
	s = s.strip('"')
	
	# produce nice spacing for boolean expressions
	s = s.replace("(", " ( ")
	s = s.replace(")", " ) ")
	
	listOfTerms = re.split('[^a-zA-Z0-9*()]+', s)
	if listOfTerms[0] == '' :
		listOfTerms.pop(0)
	if listOfTerms[len(listOfTerms) - 1] == '' :
		listOfTerms.pop()
	
	newTermList = []
	
	for term in listOfTerms :
		
		if(term == "AND" or term == "OR" or term == "(" or term == ")") :
			newTermList.append(term)
		elif term.find("*") > -1 :
			newTermList.append(term.lower())
		elif not term in stopWordSet :
			term = PorterStemmer.stemWord(pstemmer, term.lower())
			newTermList.append(term)
			
	# ignore consecutive ANDs or ORs
	lastWasBool = False
	newTermList2 = []
	for term in newTermList :
		if (term == "AND" or term == "OR") :
			if not lastWasBool :
				newTermList2.append(term)
			lastWasBool = True
		else :
			lastWasBool = False
			newTermList2.append(term)
	
	toReturn = ' '.join(newTermList2)
	if(isWrapped) :
		toReturn = '"' + toReturn + '"'
	return toReturn

# Reads from the titles file and builds a map
# from docID to title.
# input:
#	filehandle for the titles file
def readInTitles(titleFile) :

	for t in titleFile :
		fields = t.split("\t")
		
		docID = int(fields[0])
		
		# whether the header is stub-length
		stub1 = int(fields[1])
		if stub1 == 0 :
			stubsHeader[docID] = False
		else :
			stubsHeader[docID] = True
			
		# whether the body of the article is stub-length
		stub2 = int(fields[2])
		if stub2 == 0 :
			stubsBody[docID] = False
		else :
			stubsBody[docID] = True
		
		titleString = fields[3].lower()
		
		rawTitles[docID] = titleString
		
		listOfTerms = re.split('[^a-z0-9*()]+', titleString)
		if listOfTerms[0] == '' :
			listOfTerms.pop(0)
		if listOfTerms[len(listOfTerms) - 1] == '' :
			listOfTerms.pop()
		
		newListOfTerms = []
		for t in listOfTerms :
			if not t in stopWordSet:
				newListOfTerms.append(t)
			
		titleTermSet = set()
		for term in newListOfTerms :
			titleTermSet.add(PorterStemmer.stemWord(pstemmer, term))
		
		titles[docID] = titleTermSet

	
##################################################
#######   READING THE INVERTED INDEX  ############
##################################################

# take in a single postings list and return a mapping
# from docID to list of positions
def createIndex(postingString) :
	
	if (postingString == None) :
		return dict(), 0.0
	postingFields = str.split(postingString.strip(), ':')
	
	#will want this to be global weight
	idf = postingFields.pop(0)
	
	# the dictionary to return
	outDict = dict()
		
	for f in postingFields :
		innerFields = str.split(f, ' ')
		docID = int(innerFields.pop(0))
		
		positionList = []
		for p in innerFields :
			positionList.append(int(p))
		outDict[docID] = positionList
	
	return outDict, float(idf)
		
# Given a token (with or without the dollar sign),
# fetches the corresponding postings list from the
# index file.
#
# input: a stemmed term from the lexicon
def getPostingsList(token, btree, indexFile) :
	if token.find("$") == -1 :
		token = '$' + token
	if token in btree :
		bytePosition = btree[token]
		indexFile.seek(bytePosition, 0)
		line = indexFile.readline()
		return line

	

##################################################
#########     QUERY HANDLING       ###############
##################################################

# in : a string
# out : a set of docID results
def query(s, indexFile, btree, normDict, cache) :
	
	# return if invalid input
	if not len(s) > 0 :
		return set()
	
	# prepare the query string
	s = str.strip(s)
	s = preProcessString(s)

	# ensure that the string is still valid
	# after the preprocessing step
	if not len(s) > 0 :
		return set()
	if s == "*" :
		return set()
	
	# if the query is quoted, perform a phrase query
	if isWrappedInQuotes(s) :
		return phraseQuery(s, indexFile, btree, normDict, cache)
	
	tup = bool_expr_ast(s)

	if isinstance(tup, str) :

		return freeTextQuery(tup, indexFile, btree, normDict, cache)
	else :
		return boolQuery(tup, indexFile, btree, normDict, cache)


# This function returns the set of terms from the
# btree which match the single wildcard query
# input:
#	a query that contains a single "*"
# output:
#	the set of matching terms
def singleWildcard(s, indexFile, btree, normDict, cache) :
	
	# rotate the star to the beginning and then
	# get rid of it
	while(s[0] != '*'):
		s = rotateLeft(s)
	s = s[1:]
	
	# get all b tree matches
	begin = s
	end = s + "{" # because "z" < "{"
	therange = btree.keys(min=begin, max=end, excludemin=False, excludemax=True)
	
	outSet = set()
	for i in therange :
		while(i[0] != '$'):
			i = rotateLeft(i)
		outSet.add(i)
		
	return outSet

# This method is analogous to singleWildcard, except
# it works for an arbitrary number of wildcards.
#
# Works by making several calls to singleWildCard!
#
# input: a preprocessed (i.e., stemmed, lowercased, etc.)
#	wildcard query that may have any number of wildcards
# output: the set of resulting terms in the btree that
#	match
def multiWildcard(s, indexFile, btree, normDict, cache) :
	
	# base case: "*" at beginning and end
	if s[0] == "*" and s[-1] == "*" and len(s) > 1:
		s = s[0:-1] # take off the last "*"
		return singleWildcard(s, indexFile, btree, normDict, cache)
	
	else :
		outset = set()
		setIsEmpty = True
		
		wildlist = s.split("*")
		first = wildlist.pop(0)
		last = wildlist.pop()
		
		# no "*" at the beginning
		if not first == "" :
			query = "$" + first + "*"
			outset = singleWildcard(query, indexFile, btree, normDict, cache)
			setIsEmpty = False
		
		# no "*" at the end
		if not last == "" :
			query = "*" + last + "$"
			if setIsEmpty :
				outset = singleWildcard(query, indexFile, btree, normDict, cache)
				setIsEmpty = False
			else :
				outset = outset.intersection(singleWildcard(query, indexFile, btree, normDict, cache))
		
		# make recursive calls for each element in the list
		for term in wildlist :
			if term == "" :
				continue
			query = "*" + term + "*"
			if setIsEmpty :
				outset = multiWildcard(query)
				setIsEmpty = False
			else :
				outset = outset.intersection(multiWildcard(query, indexFile, btree, normDict, cache))
				
		return outset

# This function should be called directly for one word
# wildcard queries. It is called indirectly for
# other types of queries that contain wildcards.
#
# input: a preprocessed wildcard query string
# output: the list of matching docIDs
def wildcardQuery(s, indexFile, btree, normDict, cache) :

	keyset = set()
	
	if s.count("*") == 1 and len(s) > 1:
		s = s + '$'
		keyset = singleWildcard(s, indexFile, btree, normDict, cache)
	elif s.count("*") > 1 :
		keyset = multiWildcard(s, indexFile, btree, normDict, cache)

	outList = []
	for i in keyset :
		bytes = btree[i]
		indexFile.seek(bytes, 0)
		line = indexFile.readline()
		cache[i] = createIndex(line)
		dictionary = cache[i][0]
		
		outList.extend(dictionary.keys())

	return outList
	

# input: string
# output: boolean saying whether it's wrapped in quotes
# (i.e. a Phrase query)
def isWrappedInQuotes(s) :
	if s == '': 
		return False
	else :
		return s[0] == '"' and s[len(s) - 1] == '"'
	

# in : a string
# out : a list of strings. This now just splits it
def tokenizeFreeText(s) :
	listOfTerms = re.split('[^a-z0-9*]+', s)
	return listOfTerms

# in : a tuple of string 
# out : a set of the docID results
def boolQuery(tup, indexFile, btree, normDict, cache) :
	if isinstance(tup, str) :
		return freeTextQuery(tup, indexFile, btree, normDict, cache)
	else :
		boolOp, argList = tup
		resultSet = set()
		
		if boolOp == 'AND' :
			resultSet = boolQuery(argList[0], indexFile, btree, normDict, cache)
			for q in argList :
				resultSet = resultSet.intersection(boolQuery(q, indexFile, btree, normDict, cache))
			
		elif boolOp == 'OR' :
			for q in argList :
				resultSet = resultSet.union(boolQuery(q, indexFile, btree, normDict, cache))
	
		return resultSet
			

# Use this function two merge two dictionaries
# whose values are lists. If both dictionaries
# contain the same key, then append the list for
# dictionary 2 to the list of dictionary 1.
#
# Called by: phraseQuery
#
# input:
#	1. d1, the first dictionary to merge
#	2. d2. the second dictionary to merge
# output:
#	a dictionary containing the data from both
#	d1 and d2
def merge(d1, d2) :
	
	for key in d2 :
		if not key in d1 :
			d1[key] = d2[key]
		else :
			updateList = set(d1[key])
			toAdd = set(d2[key])
			updateList = updateList.union(toAdd)
			d1[key] = sorted(updateList)
	return d1
		
# This method provides phrase query functionality
# for phrase queries with and without wildcards.
# For handling wildcards, calls are made to
# the multiWildcard method.
#	
# in : a string query wrapped in quotes
# out : a list of docID results
def phraseQuery(s, indexFile, btree, normDict, cache) :
	s = str.strip(s)
	s = str.strip(s, '"')
	listOfTerms = tokenizeFreeText(s)
	tup = "AND", listOfTerms
	docIDSet = boolQuery(tup, indexFile, btree, normDict, cache)
	newDocIDSet = set()
	
	# map from docID to postings dictionary
	bigDict = dict()
	postings = dict()
	
	for term in listOfTerms :
		if term.find("*") > -1 :
			termSet = multiWildcard(term, indexFile, btree, normDict, cache)
			for t in termSet :
					nextIDDict = cache[t][0]
					postings = merge(postings, nextIDDict)
		else :
			postings = cache[term][0]

		bigDict[term] = postings
		
	
	for docID in docIDSet :
		for index, term in enumerate(listOfTerms) :
			if index < 1 :
				locationSet = set(bigDict[term][docID])
			else :
				#this intersects the position list - index with existing position list
				locationSet = locationSet.intersection(set(map((lambda x: x - index), bigDict[term][docID])))
			
		if len(locationSet) > 0 :
			newDocIDSet.add(docID)
	
	return newDocIDSet

# Function for handling free text queries.
# Handles free text queries with wildcards by
# calling wildcardQuery()
#
# input: the proceprocessed query string
# output: a list containing all of the docIDs
#	that match the free text query
def freeTextQuery(s, indexFile, btree, normDict, cache) :
	tokenList = tokenizeFreeText(s)
	
	resultSet = set()
	for t in tokenList :
		if(t.find("*") > -1) :
			postings = wildcardQuery(t, indexFile, btree, normDict, cache)
			resultSet = resultSet.union(set(postings))
		else :
			# get a dictionary from doc ID to positions
			cache[t] = createIndex(getPostingsList(t, btree, indexFile))
			postings = cache[t][0]

			resultSet = resultSet.union(set(postings.keys()))

	return resultSet

##################################################################################
############## 					RANKING						  ####################
##################################################################################


# Called as a helper to getTopK for non-wildcard
# queries. Does the scoring for one term in
# the input query.
#
# input:
#	1. term, one of the terms in the query
#	2. docScores, a map from docID to score, which
#		this function will update and return
#	3. docIDList, the list of possible matching
#		docIDs
# output:
#	the docScores map, updated to account for this
#	query term.
def updateDocScoresRegular(term, docScores, docIDList, cache, normDict) :
	term = PorterStemmer.stemWord(pstemmer, term)
	
	if not term in cache :
		return docScores
		
	thetuple = cache[term]
	
	# maps from docID to position list
	dictionary = thetuple[0]
	
	# inverse document frequency score
	idf = thetuple[1]
	
	for ID in dictionary.keys() :
		if ID in docScores and docIDList:
			docScores[ID] += (len(dictionary[ID]) * idf) / normDict[ID]
			
		elif ID in docIDList :
			docScores[ID] = (len(dictionary[ID]) * idf) / normDict[ID]
	
	return docScores

# Called as a helper to getTopK for wildcard
# queries. Does the scoring for one term in
# the input query. This term may contain any
# number of wildcards.
#
# input:
#	1. term, one of the terms in the query
#	2. docScores, a map from docID to score, which
#		this function will update and return
#	3. docIDList, the list of possible matching
#		docIDs
# output:
#	the docScores map, updated to account for this
#	query term.
def updateDocScoresWildcard(term, docScores, docIDList, cache, normDict, btree) :
	
	termSet = set()

	if term.count("*") == 1 :
		term = term + '$'
		termSet = singleWildcard(term, docScores, btree, cache, normDict)
	elif term.count("*") > 1 :
		termSet = multiWildcard(term, docScores, btree, cache, normDict)
	
	idf = 0
	termDocScores = dict()
	for t in termSet :
		
		if not t in cache :
			continue
		
		thetuple = cache[t]
		dictionary = thetuple[0]
		
		if thetuple[1] > idf :
			idf = thetuple[1]
			
		for ID in dictionary :
			if ID in termDocScores and docIDList:
				toCheck = len(dictionary[ID])
				if termDocScores[ID] < toCheck :
					termDocScores[ID] = toCheck
				
			elif ID in docIDList :
				termDocScores[ID] = len(dictionary[ID])
			
	for docID in termDocScores :
		if docID in docScores and docIDList:
			docScores[docID] += termDocScores[docID] * idf
		elif docID in docIDList :
			docScores[docID] = termDocScores[docID] * idf
	
	for ID in docScores :
		docScores[ID] = docScores[ID] / normDict[ID]
	
	return docScores

# Given a set of documents and a query, performs the ranking
# and returns the top K best matches. K is a global constant,
# usually defined as K = 10.
#
# This function performs tf-idf weighting, and then calls
# computeFinalRankings to incorporate other measures
# of relevance.
#
# input:
#	1. q, the query
#	2. docIDList, the set of documents that matches q
# output:
#	a list of the K best matches, listed in decreasing
#	order of relevance to the query
def getTopK(q, docIDList, pageRank, cache, zoneCache, normDict, zoneNorm, btree, zoneBtree) :
	scores = dict()
	
	q = q.strip()
	
	# remove AND and OR
	regex1 = re.compile("AND")
	regex2 = re.compile("OR")
	q = re.sub(regex1, "", q)
	q = re.sub(regex2, "", q)
	
	if isWrappedInQuotes(q):
		q = q.strip('"')
	listOfTerms = re.split('[^a-zA-Z0-9*]+', q.lower())
	if listOfTerms[0] == '' :
		listOfTerms.pop(0)
	if listOfTerms[-1] == '' :
		listOfTerms.pop()
	
	stopwordedTermList = []
	for t in listOfTerms :
		if not t in stopWordSet:
			stopwordedTermList.append(t)

	docScores = dict()
	zoneScores = dict()

	# compute the scores in the "normal" index
	for term in stopwordedTermList :
		if(term.find("*") > -1) :
			docScores = updateDocScoresWildcard(term, docScores, docIDList, cache, normDict, btree)
		else :
			docScores = updateDocScoresRegular(term, docScores, docIDList, cache, normDict)
	
	# compute the scores in the "zone" index, which indexes the top section
	# of each wikipedia page
	for term in stopwordedTermList :
		if(term.find("*") > -1) :
			zoneScores = updateDocScoresWildcard(term, zoneScores, docIDList, zoneCache, zoneNorm, zoneBtree)
		else :
			zoneScores = updateDocScoresRegular(term, zoneScores, docIDList, zoneCache, zoneNorm)
			
	
	# stem the query words before passing them in to the final ranking function
	queryTerms = []
	for term in stopwordedTermList :
		queryTerms.append(PorterStemmer.stemWord(pstemmer, term))
	
	return computeFinalRanking(queryTerms, docIDList, docScores, zoneScores, pageRank, cache, zoneCache)


# mnbRank
#
# Called from computeFinalRanking, this function updates document scores
# based on a text classification "majority vote" procedure.
def mnbRank(docScores, zoneScores) :
	
	classCount = dict()
	totalDocs = 0
	
	# get stats on the classifications
	for docID in docScores :
		
		totalDocs += 1
		classif = mnbClassif[docID]
		
		if classif in classCount :
			classCount[classif] += 1
		else :
			classCount[classif] = 1
	
	for docID in zoneScores :
		if not docID in docScores :
			
			totalDocs += 1
			classif = mnbClassif[docID]
			
			if classif in classCount :
				classCount[classif] += 1
			else :
				classCount[classif] = 1
			
	# map each classification to the fraction of
	# query results that have that classification
	for classif in classCount :
		classCount[classif] = float(classCount[classif]) / float(totalDocs)
		
	return classCount


# computeFinalRanking
#
# This function is an important helper for getTopK.
# This function integrates the different score measures
# in order to determine the final ranking.
#
def computeFinalRanking(listOfTerms, hits, docScores, zoneScores, pageRank, cache, zoneCache) :
	
	# get weights!
	weights = WeightHolder()
	
	# determine the generality of the query, based
	# on the inverse document frequency. The lower the
	# inverse document frequency, the more general
	# the query
	queryIdf = 0
	idfNum = 0
	for term in listOfTerms :
		if term in cache :
			queryIdf += cache[term][1]
			idfNum += 1
		if term in zoneCache :
			queryIdf += zoneCache[term][1]
			idfNum += 1
	
	if idfNum != 0 :
		queryIdf = queryIdf / float(idfNum)
	else :
		queryIdf = 10.0
	
	print "query doc freq: ", queryIdf
	
	# get classification information
	classifScores = mnbRank(docScores, zoneScores)
	
	# get the max score for each type of measurement---
	# this will be used to normalize the scores
	maxPageRank = 0
	maxTermRank = 0
	maxZoneRank = 0
	newPageRank = dict()
	for docID in hits :
		
		# compress the range of the page rankings using
		# logarithms; take the inverse in order to ensure
		# that the highest page ranks remain the highest
		if pageRank[docID] > 0 :
			newPageRank[docID] = -1.0 / math.log(pageRank[docID])
		else :
			newPageRank[docID] = 0
		
		if newPageRank[docID] > maxPageRank :
			maxPageRank = newPageRank[docID]
		
		if docID in docScores :
			if docScores[docID] > maxTermRank :
				maxTermRank = docScores[docID]
		
		if docID in zoneScores :
			if zoneScores[docID] > maxZoneRank :
				maxZoneRank = zoneScores[docID]
	
	# compute the weighted average
	weightedScore = dict()
	t1 = 0; t2 = 0; t3 = 0; t4 = 0
	
	# will store the contributions of each term
	# in the main weighting scheme
	t1d = dict(); t2d = dict(); t3d = dict(); t4d = dict()
	
	for docID in hits :
		
		###################################################
		#
		# dynamically compute weights
		#
		###################################################
		
		w1 = weights.getTermRankWeight()
		w2 = weights.getPageRankWeight()
		w3 = weights.getZoneWeight()
		w4 = weights.getMNBWeight()
		
		# If the query is general, then weight page rank higher and
		# underweight articles that are tagged as stubs.
		#
		# Equate generality of the query to high document frequency
		# of the query terms.
		if queryIdf <= weights.getIdfCutoff() :
			w1 -= 0.1
			w2 += 0.2
			w3 -= 0.1
			
		if stubsBody[docID] :
			w1 -= 0.3
			w2 += 0.15
			w3 += 0.15
			
		if stubsHeader[docID] :
			w1 += 0.05
			w2 += 0.05
			w3 -= 0.1
			
		###################################################
		
		# normalize tf-idf for text body
		if docID in docScores and maxTermRank > 0 :
			t1 = (docScores[docID] / maxTermRank)
		else :
			docScores[docID] = 0
			t1 = 0
		
		# normalize page rank
		if maxPageRank > 0 :
			t2 = (newPageRank[docID] / maxPageRank)
		else :
			t2 = 0
		
		# normalize tf-idf for "header" text
		if docID in zoneScores and maxZoneRank > 0 :
			t3 = (zoneScores[docID] / maxZoneRank)
		else :
			zoneScores[docID] = 0
			t3 = 0
		
		classif = mnbClassif[docID]
		if classif in classifScores :
			t4 = classifScores[classif]
		else :
			t4 = 0
		
		# do the weighting here
		weightedScore[docID] = (w1 * t1) + (w2 * t2) + (w3 * t3) + (w4 * t4)
								
		t1d[docID] = w1 * t1
		t2d[docID] = w2 * t2
		t3d[docID] = w3 * t3
		t4d[docID] = w4 * t4
	
	# improve the score for each matching title term
	for term in listOfTerms :
		for docID in weightedScore :
			if term in titles[docID] :
				#print "boosting due to title: ", docID
				weightedScore[docID] *= weights.getTitleBoostFactor()
	
	# reduce the score for stubs if the query is sufficiently general
	if queryIdf <= weights.getIdfCutoff() :
		print "overweighting page rank"
		for docID in weightedScore :
			if stubsBody[docID] or stubsHeader[docID] :
				weightedScore[docID] *= weights.getStubBoostFactor()
				
	# reduce the score if page rank was the major contributor
	for docID in weightedScore :
		"applying page rank control: ", docID
		if t1d[docID] > 0 :
			if (t2d[docID] / t1d[docID]) > 10.0 :
				weightedScore[docID] *= weights.getPageRankControl()
		if t3d[docID] > 0 :
			if (t2d[docID] / t3d[docID]) > 10.0 :
				weightedScore[docID] *= weights.getPageRankControl()
	
	# extract the top 10 ranked documents using a priority queue ("heapq")
	top10 = heapq.nlargest(K, sorted(weightedScore), key=(lambda x : weightedScore[x]))
			
	# =====> Uncomment if you want to see the scores and weights! <=====
	for docID in top10 :
		print docID, weightedScore[docID], t1d[docID], t3d[docID], t2d[docID], t4d[docID], mnbClassif[docID], rawTitles[docID].strip()
			
	return top10


##################################################################################
#### MULTINOMIAL NAIVE BAYES CLASSIFICATION								   #######
##################################################################################

def readMNBClassif(classifFile) :
	
	for line in classifFile :
		
		fields = line.split(" ")
		docID = int(fields[0].strip())
		classif = int(fields[1].strip())
		
		mnbClassif[docID] = classif
		
		if classif in totalInClass :
			totalInClass[classif] += 1
		else :
			totalInClass[classif] = 1
		

##################################################################################
##################################################################################
##################################################################################

###########################################################
# MAIN
#
# Reads in the filehandles, calls preprocessing functions
# for reading in the necessary data. Then enters the main
# loop, which exits when it receives CNTRL-D or EOF.
#
###########################################################
if __name__ == '__main__' :
	
	indexFile = open(sys.argv[1])
	zoneFile = open(sys.argv[2])
	stopWords = open(sys.argv[3])
	pageRankFile = open(sys.argv[4])
	titleFile = open(sys.argv[5])
	classifFile = open(sys.argv[6])


	# global dict which avoids doing unnecessary
	# disk reads. The cache should be flushed
	# before every query.
	cache = dict()
	zoneCache = dict()
	
	# global reference to the btree kept in memory
	btree = OOBTree()
	zoneBtree = OOBTree()
	
	# global map from docID to Euclidian normalization factor
	normDict = dict()
	zoneNorm = dict()
	
	# create a set of stop words from the stopWords infile
	# assuming that there is one word per line
	for line in stopWords:
		stopWordSet.add(line.strip())
	
	# construct the dictionaries as btrees
	buildDictionary(indexFile, btree, normDict)
	buildDictionary(zoneFile, zoneBtree, zoneNorm)
	
	receiveInput = True
	
	print "reading in page rank results"
	
	# read page rankings into a list
	pageRank = []
	for line in pageRankFile :
		pageRank.append(float(line))
	
	print "reading in titles"
	
	# read titles into a list
	readInTitles(titleFile)
	
	print "reading MNB classification data"
	readMNBClassif(classifFile)
	
	print "accepting queries"
	
	# main loop, receives from stdin
	while receiveInput :
		try:
			
			# flush the caches!
			cache.clear()
			zoneCache.clear()
			
			q = raw_input()
			q = q.strip()
			# make sure that input is valid
			if (line == "") :
				continue
		
			# get the set of matching documents
			docIDList = query(q, indexFile, btree, normDict, cache)
			zoneIDList = query(q, zoneFile, zoneBtree, zoneNorm, zoneCache)
			
			# merge the sets of matches
			hits = docIDList.union(zoneIDList)
			
			# do the ranking
			if(len(hits) == 0) :
				sys.stdout.write("\n")
				continue
			else:
				topKList = getTopK(q, hits, pageRank, cache, zoneCache, normDict, zoneNorm, btree, zoneBtree)
			
				strTopKList = map(str, topKList) 
				sys.stdout.write(" ".join(strTopKList))
				sys.stdout.write("\n")
		
		except EOFError:
			receiveInput = False
	
