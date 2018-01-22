#!/usr/bin/python
import sys 
import re 

def main(argv):
    for line in sys.stdin: 
      sys.stdout.write(line)

if __name__ == "__main__": 
    main(sys.argv) 
