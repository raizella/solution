import PorterStemmer
import re
import sys
from bool_parser import bool_expr_ast

# global reference to the bigDict
bigDict = dict()

# global stemmer
pstemmer = PorterStemmer.PorterStemmer()

# global set of stopWords
stopWordSet = set()


def createIndex(indexFile):
    for line in indexFile:
        fields = str.split(line, ':')

        # first field is the term
        term = fields.pop(0)

        littleDict = dict()

        for f in fields:
            postingFields = str.split(f, ' ')
            docID = int(postingFields.pop(0))
            positionList = []
            for p in postingFields:
                positionList.append(int(p))
            littleDict[docID] = positionList

        bigDict[term] = littleDict


# in : a string
# out : a set of docID results
def query(s):
    s = str.strip(s)
    if isWrappedInQuotes(s):
        return phraseQuery(s)

    tup = bool_expr_ast(s)
    if isinstance(tup, str):
        return freeTextQuery(tup)
    else:
        return boolQuery(tup)


# in: string
# out: boolean saying whether it's wrapped in quotes
# (i.e. a Phrase query)
def isWrappedInQuotes(s):
    if s == '':
        return False
    else:
        return s[0] == '"' and s[len(s) - 1] == '"'


# in : a string
# out : a list of strings that has been stemmed and stopworded
def tokenizeFreeText(s):
    listOfTerms = re.split('[^a-z0-9]+', s.lower())
    if listOfTerms[0] == '':
        listOfTerms.pop(0)
    if listOfTerms[len(listOfTerms) - 1] == '':
        listOfTerms.pop()

    newTermList = []

    for term in listOfTerms:
        if not term in stopWordSet:
            term = PorterStemmer.stemWord(pstemmer, term)
            newTermList.append(term)

    return newTermList


# in : a tuple of string
# out : a set of the docID results
def boolQuery(tup):
    if isinstance(tup, str):
        return freeTextQuery(tup)
    else:
        boolOp, argList = tup
        resultSet = set()

        if boolOp == 'AND':
            resultSet = boolQuery(argList[0])
            for q in argList:
                resultSet = resultSet.intersection(boolQuery(q))

        elif boolOp == 'OR':
            for q in argList:
                resultSet = resultSet.union(boolQuery(q))

        return resultSet


# in : a string query wrapped in quotes
# out : a list of docID results
def phraseQuery(s):
    s = str.strip(s)
    s = str.strip(s, '"')
    listOfTerms = tokenizeFreeText(s)
    tup = "AND", listOfTerms

    docIDSet = boolQuery(tup)

    newDocIDSet = set()

    for docID in docIDSet:
        locationSet = set(bigDict[listOfTerms[0]][docID])

        for index, term in enumerate(listOfTerms):
            # this intersects the position list - index with existing position list
            locationSet = locationSet.intersection(set(map((lambda x: x - index), bigDict[term][docID])))
        if len(locationSet) > 0:
            newDocIDSet.add(docID)

    return newDocIDSet


def freeTextQuery(s):
    tokenList = tokenizeFreeText(s)

    resultSet = set()
    for t in tokenList:
        if t in bigDict:
            resultSet = resultSet.union(set(bigDict[t].keys()))

    return resultSet


if __name__ == '__main__':

    stopWords = open(sys.argv[1])
    indexFile = open(sys.argv[2])
    titleIndex = open(sys.argv[3])

    # create a set of stop words from the stopWords infile
    # assuming that there is one word per line
    for line in stopWords:
        stopWordSet.add(str.strip(line))

    createIndex(indexFile)

    for q in sys.stdin:
        docIDList = sorted(query(q))
        strDocIDList = map(str, docIDList)
        sys.stdout.write(" ".join(strDocIDList))
        sys.stdout.write("\n")
