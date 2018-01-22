##################################################
#
# Authors:
#   David Storch (dstorch)
#   Matthew Mahoney (mjmahone)
#   April 2011
##################################################

import sys
import re
import math

# input:
#	1. line, a string to search
#	2. searchString, the string which we are looking for
# output:
#	The index in "line" of the rightmost character in the
#	first occurrence of searchString.
def realFind(line, searchString) :
	index = str.find(line, searchString)
	if index != -1 :
		index += len( searchString)
	return index

# The XMLParser object, given a file, is responsible
# for producing a collection of ParsedPage objects.
# Most of the work of this parsing is delegated to
# the methods of the ParsedPage objects themselves.
class XMLParser(object):
	
	# constructor
	# input: toParse, a filehandle for the
	#		file to parse
	def __init__(self, toParse) :
		self._toParse = toParse
		
	# This is the public method through which the
	# functionality of the XMLParser class should be
	# accessed. It is responsible for parsing the XML
	# of the entire collection.
	def parseCollection(self) :
		self._toParse
		while not self._toParse.closed :
			#need to catch EOF error
			line = self._toParse.readline()
			openIndex = realFind(line, "<collection>")
			if openIndex != -1 :
				return self.parsePages(line[openIndex:])
			
	# The top-level XML parsing methof which is called from
	# parse collection. This method calls the ParsedPage
	# constructor and then calls ParsedPage.parse() on this
	# object.
	def parsePages(self, restOfLine) :
		pageList = []
		
		line = restOfLine
		
		while str.find(line, "</collection>") == -1 :
			openIndex = realFind(line, "<page>")
			if openIndex != -1 :
				page = ParsedPage(self._toParse)
				page.parse(line[openIndex:])
				pageList.append(page)
		
			line = self._toParse.readline()
		
		return pageList

##########################################################################
#################### 		XML PARSING           ########################
##########################################################################

# A ParsedPage object packages the id number, title,
# and text contained within each page tag
class ParsedPage(object) :
	def __init__(self, toParse) :
		self._toParse = toParse
		self._id = -1
		self._title = ""
		self._text = ""
		
	# The main parsing method of this object.
	# Once this method returns, the _id, _title,
	# and _text attributes of this object should
	# have been set
	def parse(self, restOfLine) :
		line = restOfLine
		
		while str.find(line, "</page>") == -1 :
			
			idIndex = realFind(line, "<id>")
			titleIndex = realFind(line, "<title>")
			textIndex = realFind(line, "<text>")
			
			if idIndex != -1 :
				line = self.idParse(line[idIndex:])
			
			if titleIndex != -1:
				line = self.titleParse(line[titleIndex:])
			
			if textIndex != -1:
				line = self.textParse(line[textIndex:])
		
			line = self._toParse.readline()
	
	# Whenever we find an <id> xml tag, call this
	# method to parse everying inside the tag.
	# Sets the _id instance variable of this
	# object.
	#
	# input: a string containing the xml which immediately
	#		follows the <id> tag
	def idParse(self, restOfLine) :
		line = restOfLine
		
		pageID = ""
		
		beginIndex = str.find(line, "</id>")
		
		while beginIndex == -1 :
			pageID += line
			line = self._toParse.readline()
			beginIndex = str.find(line, "</id>")
			
			
		pageID += line[:beginIndex]
			
		# once out of the loop, we have found the id
		self._id = int(pageID)
		
		# return the text after the closing tag
		return line[beginIndex:]
	
	# This method parses everything inside a <title>
	# tag. Sets the _title instance variable
	# of this object.
	#
	# input: a string containing the xml which
	#		immediately follows the <title> tag
	def titleParse(self, restOfLine) :
		line = restOfLine
		
		pageTitle = ""
		
		beginIndex = str.find(line, "</title>")
		
		while beginIndex == -1 :
			pageTitle += line
			line = self._toParse.readline()
			beginIndex = str.find(line, "</title>")
			
			
		pageTitle += line[:beginIndex]
			
		# once out of the loop, we have found the id
		self._title = pageTitle
		
		# return the text after the closing tag
		return line[beginIndex:]
	
	# This method parses everything inside of
	# a <text> tag. Sets the _text instance
	# variable of this object.
	#
	# input:  a string containing the xml which
	#		immediately follows the <title> tag
	def textParse(self, restOfLine) :
		line = restOfLine
		
		pageText = ""
		
		beginIndex = str.find(line, "</text>")
		
		while beginIndex == -1 :
			pageText += line
			line = self._toParse.readline()
			beginIndex = str.find(line, "</text>")
			
			
		pageText += line[:beginIndex]
			
		# once out of the loop, we have found the id
		self._text = pageText
		
		# return the text after the closing tag
		return line[beginIndex:]
	
	
	# Testing method which prints out the information
	# for this ParsedPage object to the stdout
	def page_print(self) :
		print(self._id)
		print(self._title)
		print(self._text)
		 
##############################################################################################
##############################################################################################
##############################################################################################

if __name__ == '__main__' :
	
	# filehandles
	collection = open(sys.argv[1])
	outfile = open(sys.argv[2], 'w')

	# extract docID, title, and text from the XML
	xmlparse = XMLParser(collection)
	parsedPages = xmlparse.parseCollection()
	
	# the number of documents
	N = float(len(parsedPages))
	
	title2id = dict()
	adjacency = []
	
	# set up map from title to docID
	for p in parsedPages :
		title2id[p._title] = p._id
		
	# build the adjacency matrix
	for p in parsedPages :

		adjacencyList = []
		
		matches = re.findall("\[\[[^\[\]]*\]\]", p._text)
		 
		for match in matches :
			match = match[2:-2]
			
			arr = match.split("|")
			match = arr[0]
			arr = match.split("#")
			match = arr[0]
			
			if match in title2id :
				if not title2id[match] in adjacencyList :
					adjacencyList.append(title2id[match])
				
		adjacency.append(adjacencyList)
				
	# write out to the file
	for i, adjList in enumerate(adjacency) :
		if len(adjList) == 0 :
			continue
		degree = str(1.0/float(len(adjList)))
		for j in adjList :
			outfile.write(str(i+1) + " " + str(j+1) + " " + degree + "\n")

