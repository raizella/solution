###################################################
# classify.py -
#  Calls into the rocchio.py and bayes.py in order
#  to implemented Naive Multinomial Bayes and
#  Rocchio text classification algorithms.
#
# @author dstorch
# @author mjmahone
###################################################

import rocchio
import bayes
import sys

if __name__ == '__main__' :
	
	classifMethod = sys.argv[1]
	features = open(sys.argv[2])
	vecRep = open(sys.argv[3])
	training = open(sys.argv[4])
	toClassify = open(sys.argv[5])
	outfile = open(sys.argv[6], 'w')
	
	if classifMethod == "-mnb" :
		bayes.bayesClassify(features, vecRep, training, toClassify, outfile)
		
	elif classifMethod == "-r" :
		rocchio.rocchioClassify(features, vecRep, training, toClassify, outfile)


	
	