#!/usr/bin/python

from Pair import Pair
from operator import itemgetter

def main():
    pairss = [
            Pair('zebra'),
            Pair('alberto'),
            Pair('Alberto'),
            Pair('lbertoA'),
            Pair('Olya Ohrimenko'),
            Pair('web search')
            ]

    pairs = sorted(pairss, key=itemgetter(0))

    print(pairs)

    for w in pairs:
        print(w)

    alb = Pair('oalbert')

    if alb in pairs:
        print('SI')
    else:
        print('NO')

if __name__ == '__main__':
    main()

