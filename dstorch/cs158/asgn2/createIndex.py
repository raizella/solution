##################################################
#			createIndex.py
#
# Index a subset of Wikipedia, and write the
# resulting inverted index to a file. This
# index can then be queried by queryIndex.py.
#
# Arguments
#   arg1 - stop word file
#   arg2 - xml text file containing the original collection
#   arg3 - index file to output
#   arg4 - title index to output
#
# Authors:
#   David Storch (dstorch)
#   Matthew Mahoney (mjmahone)
#   March 2011
##################################################

import sys
import PorterStemmer
import re
import math


# input:
#	1. line, a string to search
#	2. searchString, the string which we are looking for
# output:
#	The index in "line" of the rightmost character in the
#	first occurrence of searchString.
def realFind(line, searchString):
    index = str.find(line, searchString)
    if index != -1:
        index += len(searchString)
    return index


# The XMLParser object, given a file, is responsible
# for producing a collection of ParsedPage objects.
# Most of the work of this parsing is delegated to
# the methods of the ParsedPage objects themselves.
class XMLParser(object):

    # constructor
    # input: toParse, a filehandle for the
    #		file to parse
    def __init__(self, toParse):
        self._toParse = toParse

    # This is the public method through which the
    # functionality of the XMLParser class should be
    # accessed. It is responsible for parsing the XML
    # of the entire collection.
    def parseCollection(self):
        self._toParse
        while not self._toParse.closed:
            # need to catch EOF error
            line = self._toParse.readline()
            openIndex = realFind(line, "<collection>")
            if openIndex != -1:
                return self.parsePages(line[openIndex:])

    # The top-level XML parsing methof which is called from
    # parse collection. This method calls the ParsedPage
    # constructor and then calls ParsedPage.parse() on this
    # object.
    def parsePages(self, restOfLine):
        pageList = []

        line = restOfLine

        while str.find(line, "</collection>") == -1:
            openIndex = realFind(line, "<page>")
            if openIndex != -1:
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
class ParsedPage(object):
    def __init__(self, toParse):
        self._toParse = toParse
        self._id = -1
        self._title = ""
        self._text = ""

    # The main parsing method of this object.
    # Once this method returns, the _id, _title,
    # and _text attributes of this object should
    # have been set
    def parse(self, restOfLine):
        line = restOfLine

        while str.find(line, "</page>") == -1:

            idIndex = realFind(line, "<id>")
            titleIndex = realFind(line, "<title>")
            textIndex = realFind(line, "<text>")

            if idIndex != -1:
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
    def idParse(self, restOfLine):
        line = restOfLine

        pageID = ""

        beginIndex = str.find(line, "</id>")

        while beginIndex == -1:
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
    def titleParse(self, restOfLine):
        line = restOfLine

        pageTitle = ""

        beginIndex = str.find(line, "</title>")

        while beginIndex == -1:
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
    def textParse(self, restOfLine):
        line = restOfLine

        pageText = ""

        beginIndex = str.find(line, "</text>")

        while beginIndex == -1:
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
    def page_print(self):
        print(self._id)
        print(self._title)
        print(self._text)


##############################################################################################
##############################################################################################
##############################################################################################

if __name__ == '__main__':

    # filehandles
    stopWords = open(sys.argv[1])
    collection = open(sys.argv[2])
    indexFile = open(sys.argv[3], 'w')
    titleIndex = open(sys.argv[4], 'w')

    # create a set of stop words from the stopWords infile
    # assuming that there is one word per line
    stopWordSet = set()
    for line in stopWords:
        stopWordSet.add(str.strip(line))

    # extract docID, title, and text from the XML
    xmlparse = XMLParser(collection)
    parsedPages = xmlparse.parseCollection()

    # maps from terms to smaller dictionaries
    bigDict = dict()

    # maps from terms to idf
    idfDict = dict()

    # maps from docID to euclidian normalization factor
    normalizationDict = dict()

    pstemmer = PorterStemmer.PorterStemmer()

    # the number of documents
    N = float(len(parsedPages))

    # set up the inverted index
    for p in parsedPages:

        docID = p._id

        # write the title index
        titleIndex.write(str(p._id) + "\t" + p._title + "\n")

        # split the terms into a list
        listOfTerms = re.split('[^a-z0-9]+', (p._title + "\n" + p._text).lower())
        if listOfTerms[0] == '':
            listOfTerms.pop(0)
        if listOfTerms[len(listOfTerms) - 1] == '':
            listOfTerms.pop()

        # build the inverted index
        index = 0
        for term in listOfTerms:
            if term in stopWordSet:
                continue
            term = PorterStemmer.stemWord(pstemmer, term)
            if term in bigDict:
                littleDict = bigDict[term]
                if docID in littleDict:
                    littleDict[docID].append(index)
                else:
                    littleDict[docID] = [index]
            else:
                bigDict[term] = dict({docID: [index]})
            index += 1

        # initialize all normalization factors to 0
        normalizationDict[docID] = 0.0

    # calculate weights
    for term in bigDict:
        idf = math.log(N / len(bigDict[term].keys()))

        littleDict = bigDict[term]
        for docID in littleDict:
            normalizationDict[docID] += len(littleDict[docID]) ** 2

        idfDict[term] = idf

    # take the square roots to get the final Euclidian normalization factors
    for docID in normalizationDict:
        normalizationDict[docID] = math.sqrt(normalizationDict[docID])

    # a map from each term to absolute position
    # in the file---we want to be able to seek
    # to the correct position in the postings list
    positionMap = dict()

    # NOTE: reserve 21 bytes for the length of the dictionary
    # (last character is a newline)

    # determine byte-positions, not taking length of header into account
    currentBytes = 0
    for term in bigDict:
        positionMap[term] = currentBytes
        littleDict = bigDict[term]
        currentBytes += len(str(idfDict[term]))
        for docID in littleDict:
            currentBytes += len(":" + str(docID))
            for pos in littleDict[docID]:
                currentBytes += len(" " + str(pos))
        currentBytes += 1

    # determine the length of the header dictionary
    dictionaryLength = 0
    for term in positionMap:
        dictionaryLength += len(term + " " + str(positionMap[term]) + "\n")

    # determine the length of the normalization dictionary
    normLength = 0
    for docID in normalizationDict:
        normLength += len(str(docID) + " " + str(normalizationDict[docID]) + "\n")

    # find length of the headers
    dictionaryLengthStr = str(dictionaryLength)
    normLengthStr = str(normLength)

    # write dictionary length to the beginning of the file
    for i in range(0, 20 - len(dictionaryLengthStr)):
        indexFile.write('0')
    indexFile.write(dictionaryLengthStr + "\n")

    # write the length of the normalization info to the beginning
    for i in range(0, 20 - len(normLengthStr)):
        indexFile.write('0')
    indexFile.write(normLengthStr + "\n")

    # write the dictionary
    for term in positionMap:
        position = positionMap[term]
        indexFile.write(term + " " + str(position) + "\n")

    # write the normalization info
    for docID in normalizationDict:
        indexFile.write(str(docID) + " " + str(normalizationDict[docID]) + "\n")

    # write the inverted index
    for term in bigDict:
        littleDict = bigDict[term]
        indexFile.write(str(idfDict[term]))
        for docID in littleDict:
            indexFile.write(":" + str(docID))
            for pos in littleDict[docID]:
                indexFile.write(" " + str(pos))
        indexFile.write("\n")
