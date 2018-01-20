##################################################
#			queryIndex.py
#
# Queries an inverted index produced by createIndex.py.
# Uses a vector space ranking model to return the doctIDs
# of the top K hits.
#
# Arguments
#   arg1 - stop word file
#   arg2 - inverted index file
#   arg3 - title index file
#
# Authors:
#   David Storch (dstorch)
#   Matthew Mahoney (mjmahone)
#   March 2011
##################################################

import PorterStemmer
import re
import sys
import heapq
from bool_parser import bool_expr_ast
from BTrees.OOBTree import OOBTree

##################################################
# GLOBAL VARIABLES
##################################################

# global constant---number of docs to retrieve
K = 10

# global reference to the btree kept in memory
btree = OOBTree()

# global map from docID to Euclidian normalization factor
normDict = dict()

# global stemmer
pstemmer = PorterStemmer.PorterStemmer()

# global set of stopWords
stopWordSet = set()

# global reference to the inverted index
indexFile = 0

# global dict which avoids doing unnecessary
# disk reads. The cache should be flushed
# before every query.
cache = dict()

# keep the titles so we can print them out in
# the results section
titles = dict()

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
def makePermuterms(s, num) :
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
def buildDictionary(indexFile) :
	dictionaryBytes = long(indexFile.readline())
	normBytes = long(indexFile.readline())
	
	# build the permuterm btree
	dictionaryString = indexFile.read(dictionaryBytes)
	dictionaryList = dictionaryString.split('\n')
	for line in dictionaryList :
		if len(line) > 1 :
			fields = line.split(' ')
			makePermuterms(fields[0], long(fields[1]) + 42 + dictionaryBytes + normBytes)

			
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
def getPostingsList(token) :
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
def query(s) :
	
	# return if invalid input
	if not len(s) > 1 :
		return ""
	

	# prepare the query string
	s = str.strip(s)
	s = preProcessString(s)

	# return if invalid input
	if not len(s) > 1 :
		return ""
	
	if isWrappedInQuotes(s) :
		return phraseQuery(s)
	
	tup = bool_expr_ast(s)

	if isinstance(tup, str) :

		return freeTextQuery(tup)
	else :
		return boolQuery(tup)


# This function returns the set of terms from the
# btree which match the single wildcard query
# input:
#	a query that contains a single "*"
# output:
#	the set of matching terms
def singleWildcard(s) :
	
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
def multiWildcard(s) :
	
	# base case: "*" at beginning and end
	if s[0] == "*" and s[-1] == "*" and len(s) > 1:
		s = s[0:-1] # take off the last "*"
		return singleWildcard(s)
	
	else :
		outset = set()
		setIsEmpty = True
		
		wildlist = s.split("*")
		first = wildlist.pop(0)
		last = wildlist.pop()
		
		# no "*" at the beginning
		if not first == "" :
			query = "$" + first + "*"
			outset = singleWildcard(query)
			setIsEmpty = False
		
		# no "*" at the end
		if not last == "" :
			query = "*" + last + "$"
			if setIsEmpty :
				outset = singleWildcard(query)
				setIsEmpty = False
			else :
				outset = outset.intersection(singleWildcard(query))
		
		# make recursive calls for each element in the list
		for term in wildlist :
			if term == "" :
				continue
			query = "*" + term + "*"
			if setIsEmpty :
				outset = multiWildcard(query)
				setIsEmpty = False
			else :
				outset = outset.intersection(multiWildcard(query))
				
		return outset

# This function should be called directly for one word
# wildcard queries. It is called indirectly for
# other types of queries that contain wildcards.
#
# input: a preprocessed wildcard query string
# output: the list of matching docIDs
def wildcardQuery(s) :

	keyset = set()
	
	if s.count("*") == 1 and len(s) > 1:
		s = s + '$'
		keyset = singleWildcard(s)
	elif s.count("*") > 1 :
		keyset = multiWildcard(s)

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
def boolQuery(tup) :
	if isinstance(tup, str) :
		return freeTextQuery(tup)
	else :
		boolOp, argList = tup
		resultSet = set()
		
		if boolOp == 'AND' :
			resultSet = boolQuery(argList[0])
			for q in argList :
				resultSet = resultSet.intersection(boolQuery(q))
			
		elif boolOp == 'OR' :
			for q in argList :
				resultSet = resultSet.union(boolQuery(q))
	
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
def phraseQuery(s) :
	s = str.strip(s)
	s = str.strip(s, '"')
	listOfTerms = tokenizeFreeText(s)
	tup = "AND", listOfTerms
	docIDSet = boolQuery(tup)
	newDocIDSet = set()
	
	# map from docID to postings dictionary
	bigDict = dict()
	postings = dict()
	
	for term in listOfTerms :
		if term.find("*") > -1 :
			termSet = multiWildcard(term)
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
def freeTextQuery(s) :
	tokenList = tokenizeFreeText(s)
	
	resultSet = set()
	for t in tokenList :
		if(t.find("*") > -1) :
			postings = wildcardQuery(t)
			resultSet = resultSet.union(set(postings))
		else :
			# get a dictionary from doc ID to positions
			cache[t] = createIndex(getPostingsList(t))
			postings = cache[t][0]

			resultSet = resultSet.union(set(postings.keys()))

	return resultSet

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
def updateDocScoresRegular(term, docScores, docIDList) :
	term = PorterStemmer.stemWord(pstemmer, term)
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
def updateDocScoresWildcard(term, docScores, docIDList) :
	
	termSet = set()

	if term.count("*") == 1 :
		term = term + '$'
		termSet = singleWildcard(term)
	elif term.count("*") > 1 :
		termSet = multiWildcard(term)
	
	idf = 0
	termDocScores = dict()
	for t in termSet :
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
# input:
#	1. q, the query
#	2. docIDList, the set of documents that matches q
# output:
#	a list of the K best matches, listed in decreasing
#	order of relevance to the query
def getTopK(q, docIDList) :
	scores = dict()
	
	q = q.strip()
	if isWrappedInQuotes(q):
		q = q.strip('"')
	listOfTerms = re.split('[^a-zA-Z0-9*]+', q.lower())
	if listOfTerms[0] == '' :
		listOfTerms.pop(0)
	if listOfTerms[-1] == '' :
		listOfTerms.pop()
	
	for t in listOfTerms :
		if t in stopWordSet:
			listOfTerms.remove(t)

	docScores = dict()

	for term in listOfTerms :
		if(term.find("*") > -1) :
			docScores = updateDocScoresWildcard(term, docScores, docIDList)
		else :
			docScores = updateDocScoresRegular(term, docScores, docIDList)
	
	#the comparison SHOULD be >, not >=
	top10 = heapq.nlargest(K, sorted(docScores), key=(lambda x : docScores[x]))
	
	# =====> Uncomment if you want to see the scores! <=====
	for ID in top10 :
		print ID, docScores[ID], titles[ID]
		
	return top10

##################################################################################
##################################################################################
##################################################################################

if __name__ == '__main__' :
	
	stopWords = open(sys.argv[1])
	indexFile = open(sys.argv[2])
	titleIndex = open(sys.argv[3])
	
	# create a set of stop words from the stopWords infile
	# assuming that there is one word per line
	for line in stopWords:
		stopWordSet.add(str.strip(line))
	buildDictionary(indexFile)
	receiveInput = True
	
	# read in titles (for printing only)
	for line in titleIndex :
		fields = line.split("\t")
		docID = int(fields[0])
		titles[docID] = fields[1].strip()
	
	# main loop, receives from stdin
	while receiveInput :
		try:
			
			# flush the cache!
			cache.clear()
			
			q = raw_input()
			q = q.strip()
			# make sure that input is valid
			if (line == "") :
				continue
		
			# get the set of matching documents
			docIDList = query(q)
			
			# do the ranking
			if(len(docIDList) == 0) :
				sys.stdout.write("\n")
				continue
			else:
				topKList = getTopK(q, docIDList)
			
				strTopKList = map(str, topKList) 
				sys.stdout.write(" ".join(strTopKList))
				sys.stdout.write("\n")
		
		except EOFError:
			receiveInput = False
		except NameError:
				sys.stdout.write("\n")
	
