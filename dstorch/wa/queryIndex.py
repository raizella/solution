#!/usr/bin/python

from Pair import Pair
import sys

def main():
    words = []

    file = open(sys.argv[1], 'r')
    try:
        for line in file:
            s = line.replace('\n','').replace('\r','')
            currentWord = Pair(s)
            words += [currentWord]
    except EOFError:
        file.close()

    while True:
        try:
            line = raw_input()
            if line:
                q = Pair(line)
                if q in words:
                    i = words.index(q)
                    #str = q.getWord() + ' => '
                    str = ''
                    while i < len(words) and words[i] == q:
                        str = str + words[i].getWord() + '|'
                        i += 1
                    print(str)
                else:
                    #print(q.getWord() + ' => ')
                    print('')
        except EOFError:
            break

if __name__ == '__main__':
    main()

