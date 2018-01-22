#!/usr/bin/python
import sys 
import re 

def main(argv): 
    i = 0
    for line in sys.stdin: 
        i += 1

        if i < 100000:
            sys.stdout.write(line)

if __name__ == "__main__": 
    main(sys.argv) 
