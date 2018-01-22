#!/usr/bin/python

###################################################
#                createIndex.py                   #
#						  #
# Given dictionary terms from the standard in,    #
# creates an "index" which stores each word in    #
# association with its ASCII-sorted anagram.      #
# This index is sorted and then printed to the    #
# standard output in the following format:        #
# asciisort(word)|word                            #
#						  #
# Arguments: none				  #
#						  #
# Author: David Storch                            #
#         login - dstorch			  #
#         2 Feb 2011				  #
###################################################

# for IO
import sys

# to create a hashmap whose values are lists
from collections import defaultdict

# mapping from anagram to list of dictionary words
index = defaultdict(list)

# set to false one EOF is received
receiveInput = True

# get input line by line from stdin
while receiveInput:
	try:
		dict_term = raw_input()
		char_list = sorted(list(dict_term))
		anagram = ""
		for s in char_list:
			anagram += s
		index[anagram].append(dict_term)
	except EOFError:
		receiveInput = False

# sort the dictionary by key
sorted_key_list = sorted(index)

# iterate over the dictionary and print the result
for key in sorted_key_list:
	
	# get a sorted version of the dictionary terms
	# corresponding to this key
	sorted_dict_terms = sorted(index[key])
	
	for s in sorted_dict_terms:
		sys.stdout.write(key)
		sys.stdout.write("|")
		sys.stdout.write(s)
		sys.stdout.write("\n")


