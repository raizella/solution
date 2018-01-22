#!/usr/bin/python

from Pair import Pair
from operator import itemgetter

def main():
    words = []
    while True:
        try:
            line = raw_input()
            if line:
                currentWord = Pair(line)
                words += [currentWord]
        except EOFError:
            break
    words = sorted(words, key=itemgetter(1))
    words = sorted(words, key=itemgetter(0))
    for word in words:
        s1 = word.getJoined().replace('\r','')
        s2 = word.getWord()
        print(s1 + '|' + s2)

if __name__ == '__main__':
    main()

