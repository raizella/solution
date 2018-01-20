#!/bin/bash

# Main program to be executed
MAIN="queryIndex.py"

# the zone index (index for the top section
# of each wiki page
ZONE="zone.out"

# the stop words file (listed one per line)
STOP="stopWords.out"

# the page rankings, listed in order of docID,
# one per line
RANK="pageRank.out"

# the titles file
TITLES="titles.out"

# the file containing document classifications
CLASSIF="classifMNB.dat"

# Call $MAIN and pass all the script arguments
python $MAIN $1 $ZONE $STOP $RANK $TITLES $CLASSIF

