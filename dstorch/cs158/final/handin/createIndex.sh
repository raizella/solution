#!/bin/bash

######################################################
# createIndex.sh -
#   The main program for generating the inverted
#   index for a Wikipedia search engine. The index
#   can then be queried by queryIndex.sh.
#
# The following python scripts are required:
#   1. buildAdjacency.py - producing the adjacency matrix
#      for the wikipedia web graph
#   2. computePageRank.sh - uses the adjacency matrix
#      to calculate page ranks; just invokes the matlab
#      script computePageRank.m
#   3. buildStopWordList.py - analyzes the collection
#      in order to determine a good list of stop words
#
# Run as:
#   ./createIndex.sh <collection> <index to output>
#
# Author:
#  David Storch
#  Brown University
#  May 2011
#
###################################################### 


STOPOUT="stopWords.out"
STOPBUILD="buildStopWordList.py"

# the stop words list builder
# and its outfile
# ====> UNCOMMENT TO AUTO-GENERATE STOP WORDS
# python $STOPBUILD $1 $STOPOUT

# Main program to be executed
MAIN="createIndex.py"

# adjacency matrix builder and outfile
ADJBUILD="buildAdjacency.py"
ADJOUT="adjacency.out"

# titles file to write
TITLES="titles.out"

# the inverted index for the main zone of the wiki pages
ZONE="zone.out"

# Call $MAIN and pass all the script arguments
python $MAIN $1 $2 $STOPOUT $TITLES $ZONE

# build the adjacency matrix
python $ADJBUILD $1 $ADJOUT

# compute page ranks
source computePageRank.sh

