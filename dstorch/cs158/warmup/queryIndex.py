#!/usr/bin/python

###################################################
#                 queryIndex.py                   #
#						  #
# For each input query, returns all anagrams	  #
# of the query extracted from the index.          #
# Queries are accepted from the standard input    #
# until receiving CNTL-D or EOF.		  #
#						  #
# Arguments:					  #
#   arg0 - A text file containing a series of	  #
#          queries. The anagrams corresponding    #
#          to each of these queries will be       #
#          printed to the standard output.        #
#						  #
# Author: David Storch                            #
#         login - dstorch			  #
#         2 Feb 2011				  #
###################################################


import sys

# for creating a hashmap whose values are lists
from collections import defaultdict

# set to false once EOF is received
receiveInput = True

# get the first argument (the file name)
file_name = sys.argv[1]

# mapping from anagram to list of dictionary words
index = defaultdict(list)

# open a reader for the file
try:
	f = open(file_name)
	for line in f:
		words = line.split("|")
		# add to the dictionary here; use the strip()
		# function to get rid of unwanted whitespace
		index[words[0]].append(words[1].strip())
except IOError:
	# named file does not exist
	print "Could not find query file."
	receiveInput = False
	


# get input line by line from stdin
while receiveInput:
	try:
		# get input
		query = raw_input()
		
		# create asciisort of the query
		char_list = sorted(list(query))
		anagram_query = ""
		for s in char_list:
			anagram_query += s
		
		# use the dictionary to find all values associated
		# with the key (anagram_query)
		for s in index[anagram_query]:
			sys.stdout.write(s)
			sys.stdout.write("|")
		
		# done with this query
		sys.stdout.write("\n")

		
	except EOFError:
		# exit the loop after receiving EOF
		receiveInput = False
		
