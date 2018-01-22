######################################################################
# bayes.py -
#  The module for performing Rocchio training and classification.
#
# This module should be used publicly by calling rocchioClassify
# with the appropriate filehandles.
#
# Note that all vectors are sparse vectors, and therefore are
# represented as dictionaries, with vector index mapping to the
# value for that index. Zero entries are omitted. Also note that
# vectors are immutable in the sense that the implemented vector
# functions return new vectors rather than mutating existing ones.
#
# @author dstorch
# @author mjmahone
######################################################################

import math

# GLOBALS
numDocs = 0

# bayesClassify()
# The main method for the bayes module, which should be called
# by the classify.py program.
# 
# args
#  1. features - a filehandle for the list of features
#  2. vecRep - a filehandle for the vector representation produced
#       by vecrep.py
#  3. training - a filehandle for the training dataset
#  4. toClassify - a filehandle for the file containing the docIDs to
#		attempt to classify and the expected results
#  5. outfile - the filehandle to which we write out our classifications
def bayesClassify(features, vecRep, training, toClassify, outfile) :
	
	# read in files for training
	featureList = readFeatures(features)
	# dict of docID -> feature vector
	bigDict = readVecRep(vecRep)
	trainingDict = readTrainingData(training)
	
	# compute probabilities based on training data
	priorDict, condProbDict = computeProbabilities(featureList, bigDict, trainingDict)
	
	# apply the multinomial naive bayes classification to the test dataset
	classifiedDocs, testData = classifyDocs(bigDict, priorDict, condProbDict, toClassify)
	
	# write to the output file
	idsToWrite = sorted(classifiedDocs.keys())
	for i in idsToWrite :
		outfile.write(str(i) + " " + str(classifiedDocs[i]) + "\n")
	
# readFeatures
# Given a filehandle for the features file, reads in
# the features, and returns a list of features.
def readFeatures(features) :
	toReturn = []
	for line in features :
		line = line.strip()
		toReturn.append(line)
	return toReturn

# readVecRep
# Given the output of vecrep.py, builds
# a dictionary of vectors, where each vector
# is keyed by its docID.
#
# Also builds the "normalization dictionary"---
# a dictionary in which the docID maps to the sum
# of the squares of the vector components.
def readVecRep(vecRep) :
	bigDict = dict()
	for line in vecRep :
		global numDocs
		numDocs += 1
		
		littleDict = dict()
		
		fields = line.split(" ")
		docID = int(fields[0])
		fields = fields[2:]
		
		for pair in fields :
			pair = pair.strip()
			pair = pair.split(":")
			littleDict[int(pair[0])] = int(pair[1])
			
		bigDict[docID] = littleDict
		
	return bigDict

# readTrainingData
# arg - a filehandle for the training data set
# 
# Returns a dictionary where each class number maps to
def readTrainingData(training) :
	trainingDict = dict()
	for line in training :
		fields = line.split(" ")
		docID = int(fields[0])
		classification = int(fields[1])
		
		if classification in trainingDict :
			trainingDict[classification].append(docID)
		else :
			trainingDict[classification] = [docID]
	
	return trainingDict

# readTestData
# Reads in the data that we need to classify.
# Returns a dictionary in which the keys are the
# docIDs to classify, and the values are the expected
# classifications.
def readTestData(toClassify) :
	testData = dict()
	for line in toClassify :
		fields = line.split(" ")
		docID = int(fields[0].strip())
		classification = int(fields[1].strip())
		testData[docID] = int(classification)
	return testData

# computeProbabilities()
# This is the function which is responsible for computing the
# "training probabilities" which are required in order to
# apply the Bayes classification to unseen data.
def computeProbabilities(featureList, bigDict, trainingDict) :
	priorDict = dict()
	condProbDict = dict()
	global numDocs
	numFeatures = len(featureList)
	for c in trainingDict :
		Nc = len(trainingDict[c])
		priorDict[c] = float(Nc)/float(numDocs)
		
		TctSum = 0
		condProbDict[c] = dict()
		
		term2tct = dict()
		for i, term in enumerate(featureList) :
			Tct = 0
			for docID in trainingDict[c] :
				if docID in bigDict :
					if i in bigDict[docID] :
						Tct += bigDict[docID][i]
			term2tct[i] = Tct
			TctSum += Tct
		
		for i in term2tct :
			condProbDict[c][i] = float(term2tct[i] + 1) / float(TctSum + numFeatures)
			
	return (priorDict, condProbDict)
			
	
def maxClass(scoreDict) :
	
	#score, docID
	maximum = float('-infinity'), float('-infinity')
	for cat in scoreDict :
		if scoreDict[cat] > maximum[0] :
			maximum = scoreDict[cat], cat
	
	return maximum[1]

# classifyDocs
# Runs the multinomial naive bayes algorithm, using the results
# from the training stage.
def classifyDocs(bigDict, priorDict, condProbDict, toClassify) :
	
	classifiedDocs = dict()
	testData = dict()
	
	for line in toClassify :
		lineArgs = line.split(" ")
		docID = int(lineArgs[0])
		classification = classifyOneDoc(docID, priorDict, condProbDict, bigDict)
		classifiedDocs[docID] = classification
	
		testData[docID] = int(lineArgs[1])
	
	return classifiedDocs, testData

# classifyOneDoc
# This method determines the MNB classification for
# a single docID.
def classifyOneDoc(docID, priorDict, condProbDict, bigDict) :
	score = dict()
	for c in priorDict :
		score[c] = math.log(priorDict[c])
		if docID in bigDict:
			for termID in bigDict[docID] :
				smallDict = condProbDict[c]
				if termID in condProbDict[c]:
					score[c] += math.log(smallDict[termID])
						
	maxCat = maxClass(score)
	return maxCat
