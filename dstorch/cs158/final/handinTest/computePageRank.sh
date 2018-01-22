#!/bin/bash

#################################################
# computePageRank.sh
#
# Use this script to execute the Matlab script
# computePageRank.m from the command line.
# See comments in computePageRank.m for more
# details.
#
# Author: David Storch (dstorch)
#################################################


# executes the Matlab script
nohup \matlab -nojvm -nodisplay < computePageRank.m &> .tmp

# delete a temp file
rm -f nohup.out
rm -f .tmp

