#!/usr/local/bin/bash


# create the compressed files
time ./compressor.sh /course/cs158/data/compression/contestPostings.dat.np compressed.np
time ./compressor.sh /course/cs158/data/compression/contestPostings.dat.p compressed.p

# create query files
python numbers.py 616723 > numbers.dat

# decompress
time ./query.sh compressed.np < numbers.dat > decompressed.np
time ./query.sh compressed.p < numbers.dat > decompressed.p

# check OK
echo diff1
diff /course/cs158/data/compression/contestPostings.dat.np decompressed.np 
echo diff2
diff /course/cs158/data/compression/contestPostings.dat.p decompressed.p

