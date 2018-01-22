######################################################################
# rocchio.py -
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
import copy

# rocchioClassify()
# The main method for the rocchio module, which should be called
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
def rocchioClassify(features, vecRep, training, toClassify, outfile) :
	# read in files for training
	featureList = readFeatures(features)
	dictTuple = readVecRep(vecRep)
	bigDict, normDict = dictTuple
	trainingDict = readTrainingData(training)
	
	# do the training
	centroidDict = trainRocchio(featureList, bigDict, normDict, trainingDict)
	
	# read in the list of documents to classify, and the expected results
	testData = readTestData(toClassify)
	
	# run the classification and collect statistics
	classifications = applyRocchio(testData, centroidDict, bigDict, normDict)
	
	# write the output
	writeResults(outfile, classifications)
	
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
	normDict = dict()
	for line in vecRep :
		
		littleDict = dict()
		
		# parse the line from the vecrep file
		fields = line.split(" ")
		docID = int(fields[0])
		normDict[docID] = int(fields[1])
		fields = fields[2:]
		
		for pair in fields :
			pair = pair.strip()
			pair = pair.split(":")
			littleDict[pair[0]] = int(pair[1])
			
		bigDict[docID] = littleDict
		
	return bigDict, normDict

# readTrainingData
# arg - a filehandle for the training data set
# 
# Returns a dictionary where each class number maps to
# a list of docIDs belonging to that classification.
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

# trainRocchio()
# The top-level function for training the Rocchio classifier, i.e.,
# computing the centroid vectors for each class.
#
# args -
#  1. featureList - the list of features used in the vector representation
#  2. bigDict - the dictionary of vectors produced by readVecRep
#  3. normDict - the dictionary containing vector normalization data
#     produced by readVecRep
#  4. trainingDict - the dictionary mapping from class to docIDs in that class
#
# return -
#  a dictionary of centroid vectors, where the keys are the classes. The class
#  maps to the centroid vector for that class
def trainRocchio(featureList, bigDict, normDict, trainingDict) :
	centroidDict = dict()
	for classification in trainingDict :
		centroidDict[classification] = computeCentroid(trainingDict[classification], bigDict, normDict)
	return centroidDict

# computeCentroid()
# Given a list of docIDs that have been classified under a certain class in
# the training set, compute the centroid vector.
#
# args -
#  1. docIDList - the list of docIDs in a given class
#  2. bigDict - the dictionary of vectors produced by readVecRep
#  3. normDict - the dictionary containing vector normalization data
#     produced by readVecRep
#
# return -
#  the centroid vector for the class from the training set containing
#  the docIDs from docIDList
def computeCentroid(docIDList, bigDict, normDict) :	
	centroid = dict()
	vectorList = []
	for docID in docIDList :
		if docID in normDict :
			normalization = math.sqrt(normDict[docID])
			normedVector = divideVector(bigDict[docID], normalization)
			vectorList.append(normedVector)
	for vector in vectorList :
		centroid = sumVector(centroid, vector)
	centroid = divideVector(centroid, float(len(docIDList)))
	return centroid

# divideVector
# args -
#  1. vector - the vector to divide
#  2. div - the scalar to divide the vector by
def divideVector(vector, div) :
	outVec = dict()
	for feature in vector :
		outVec[feature] = vector[feature]/div
	return outVec

# multiplyVector
# args -
#  1. vector - the vector to multiply
#  2. mult - the scalar to multiply the vector by
def multiplyVector(vector, mult) :
	outVec = dict()vim res	
	for feature in vector :
		outVec[feature] = vector[feature]*mult
	return outVec

# subtractVector
# args -
#  1, v1 - minuend
#  2. v2 - subtrahend
def subtractVector(v1, v2) :
	toSubtract = multiplyVector(v2, -1)
	return sumVector(v1, toSubtract)

# sumVector
# Returns a new vector, (v1 + v2)
def sumVector(v1, v2) :
	sum = dict()
	for feature in v1 :
		if feature in v2 :
			sum[feature] = v1[feature] + v2[feature]
		else :
			sum[feature] = v1[feature]
	
	# features in v2 but not v1
	for feature in v2 :
		if not feature in v1 :
			sum[feature] = v2[feature]
	
	return sum
	
# length
# Returns the length of vector v.
def length(v) :
	squareSum = 0
	for feature in v :
		squareSum += (v[feature] * v[feature])
	return math.sqrt(squareSum)

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

# applyRoccio
# Using the training results, apply the classification
# to the testData dictionary returned by readTestData
#
# args -
#  1. testData - the dictionary of docIDs to classify
#  2. centroidDict - the mapping from class to centroid vector
#  3. bigDict - the complete dictionary of vectors
#  4. normDict - the dictionary storing vector normalization data
#
# return -
#  a mapping from each docID in testData to the classification
#  produced by applyRocchioOnce
def applyRocchio(testData, centroidDict, bigDict, normDict) :
	numCorrect = 0
	numClassified = 0
	numNotClassified = 0
	classifications = dict()
	
	for docID in testData :
		if docID in bigDict :
			vector = bigDict[docID]
			normalization = normDict[docID]
			classification = applyRocchioOnce(centroidDict, vector, normalization)
			classifications[docID] = classification
			
			if classification == testData[docID] :
				numCorrect += 1
			
			numClassified += 1
		else :
			numNotClassified += 1
	
	# print some stats to the terminal
	print "percent correct: ", (float(numCorrect)/float(numClassified)) * 100
	print "number classified: ", numClassified
	print "number correct: ", numCorrect
	print "number not classified: ", numNotClassified
	
	return classifications

# applyRocchioOnce
# args -
#  1. centroidDict - the mapping from class to centroid vector
#  2. vector - the vector to classify
#  3. normalization - the square of the Euclidian normalization factor
def applyRocchioOnce(centroidDict, vector, normalization) :
	bestClass = -1
	bestDistance = ()
	
	# normalize the document vector we are classifying
	v = divideVector(vector, math.sqrt(normalization))
	
	for classification in centroidDict :
		difference = subtractVector(v, centroidDict[classification])
		diffLength = length(difference)
		if diffLength < bestDistance :
			bestClass = classification
			bestDistance = diffLength
	
	return bestClass

# writeResults
# Write out the Rocchio classifications to the output file.
def writeResults(outfile, classifications) :
	sortedIDList = sorted(classifications.keys())
	for docID in sortedIDList :
		outfile.write(str(docID) + " " + str(classifications[docID]) + "\n")	
	