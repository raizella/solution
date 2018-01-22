#!/bin/bash

############################################
# buildAdjacency.sh
#
# Run as:
#  ./buildAdjacency.sh <input collection>
#
# Use this script to calculate the page rank
# adjacency matrix.
#
############################################


# Main program to be executed
MAIN="buildAdjacency.py"

# call python script, always putting the
# output into "adjacency.dat"
python $MAIN $1 adjacency.dat

