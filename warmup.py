from typing import List


# Grading comments: performance, memory usage, etc.


def create_index(filepath: str) -> List[str]:
    """Reads the dictionary file at the given path returns
    a list of the words in the file, with newline characters
    stripped.
    """
    with open(filepath) as f:
        index = []
        for line in f:
            word = line.rstrip('\n')
            sorted_word = ''.join(sorted(word))
            index.append('{}|{}'.format(sorted_word, word))
    index.sort()
    return index


def query_index(index: List[str], query: str) -> str:
    """Takes in an index and a query, then returns the result
    of the query as a str.
    """
    sorted_query = ''.join(sorted(query))
    anagrams = [row.split('|')[1] for row in index
                if sorted_query == row.split('|')[0]]
    anagrams.sort()
    result = ''
    for anagram in anagrams:
        result += anagram
        result += '|'
    return result


def test_index():
    index = create_index('data/warmup/largeDictionary.txt')
    with open('data/warmup/largeQueries.txt') as f1:
        with open('data/warmup/largeAnagrams.txt') as f2:
            for line in f1:
                expected = f2.readline().rstrip('\n')
                assert expected == query_index(index, line.rstrip('\n'))
