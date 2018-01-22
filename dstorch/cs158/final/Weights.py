################################################################
# Weights.py -
#  a class to neatly package the constants used in the
#  search engine's ranking algorithm
#
# Author:
#  David Storch
#  login - dstorch
#  May 2011
#
################################################################

# a class to contain the weighting
# parameters for the search engine
class WeightHolder(object):
	
	def __init__(self) :
		
		# weight for pageRank
		self.pageRankWeight = 0.1

		# weight for tf-idf score in the body
		# of the document
		self.termRankWeight = 0.4

		# weight for tf-idf score in the header
		# of the document
		self.zoneWeight = 0.45
		
		# multiply the score by this factor
		# for every matching title term
		self.titleBoostFactor = 1.3

		# multiply the score by this factor
		# if the document is tagged as a stub
		self.stubBoostFactor = 0.8
	
		# overweight pagerank if the average idf of
		# the query terms is less than this value
		self.idfCutoff = 3.8
		
		# the number of words that the bottom sections
		# of characters the bottom sections of the wiki
		# page must exceed in order to not be considered a stub
		self.minimumStubChars = 1000
		
		# the factor by which we multiply if the weightings
		# suggest that page rank unnaturally affected the results
		self.pageRankControl = 0.5
		
		# the weight to give MNB classification
		self.mnbWeight = 0.05
	
	#######################################
	# GETTERS
	#######################################
	
	def getPageRankWeight(self) :
		return self.pageRankWeight
	
	def getTermRankWeight(self) :
		return self.termRankWeight
		
	def getZoneWeight(self) :
		return self.zoneWeight
	
	def getMNBWeight(self) :
		return self.mnbWeight
	
	def getTitleBoostFactor(self) :
		return self.titleBoostFactor
	
	def getStubBoostFactor(self) :
		return self.stubBoostFactor
	
	def getIdfCutoff(self) :
		return self.idfCutoff
	
	def getMinimumStubChars(self) :
		return self.minimumStubChars
	
	def getPageRankControl(self) :
		return self.pageRankControl
	
	#######################################