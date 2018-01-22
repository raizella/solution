####################################################
# makeResults.py
#
# This script is used to generate labelsSVM.dat
# based on the 11 predictionX.dat files outputted
# by svm_classify.
#
# Authors: David Storch (dstorch)
#          Matt Mahoney (mjmahone)
####################################################

import sys

if __name__ == '__main__' :


	epsilon = float(sys.argv[1])
    
	output = open("labelSVM.dat", "w")
	
	# produce an array of filehandles
	filehandles = []
	for i in range(0, 10) :
		filehandles.append(open("prediction"+str(i)+".dat"))


	lineArrays = []
	for file in filehandles :
		thisLineArray = []
		for line in file :
			thisLineArray.append(line)
		lineArrays.append(thisLineArray)
		
	for i, line in enumerate(lineArrays[0]) :
		thisLine = ""
		for filenum, array in enumerate(lineArrays) :
			value = float(array[i].strip())
			if (value > epsilon) :
				thisLine += str(filenum) + " "
		thisLine = thisLine.strip()
		output.write(thisLine + "\n")
	
