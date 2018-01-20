import sys
import PorterStemmer
import re


def realFind(line, searchString):
    index = str.find(line, searchString)
    if index != -1:
        index += len(searchString)
    return index


class XMLParser(object):
    def __init__(self, toParse):
        self._toParse = toParse

    # returns list of parsed pages
    def parseCollection(self):
        self._toParse
        while not self._toParse.closed:
            # need to catch EOF error
            line = self._toParse.readline()
            openIndex = realFind(line, "<collection>")
            if openIndex != -1:
                return self.parsePages(line[openIndex:])

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

# A ParsedPage object packages the id number, title,
# and text contained within each page tag
class ParsedPage(object):
    def __init__(self, toParse):
        self._toParse = toParse
        self._id = -1
        self._title = ""
        self._text = ""

    # the main parsing method of this object
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

    def page_print(self):
        print(self._id)
        print(self._title)
        print(self._text)


##############################################################################################
if __name__ == '__main__':
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

    bigDict = dict()

    # index = 0

    pstemmer = PorterStemmer.PorterStemmer()

    # set up the inverted index
    for p in parsedPages:
        # print "working on: " + str(p._id)

        docID = p._id
        # write the title index
        titleIndex.write(str(p._id) + "\t" + p._title + "\n")

        # index += 1
        # split the terms into a list to walk through
        listOfTerms = re.split('[^a-z0-9]+', (p._title + "\n" + p._text).lower())
        if listOfTerms[0] == '':
            listOfTerms.pop(0)
        if listOfTerms[len(listOfTerms) - 1] == '':
            listOfTerms.pop()

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

    # print the inverted index
    for term in bigDict:
        indexFile.write(term)
        littleDict = bigDict[term]
        for docID in littleDict:
            indexFile.write(":" + str(docID))
            for pos in littleDict[docID]:
                indexFile.write(" " + str(pos))
        indexFile.write("\n")
