"""
This implementation of a search engine is composed of three classes:

    - an analyzer, which converts streams of text into a list of terms
    - an index, which can parse to create an index as well as persist the index
    - a query, which is
"""

import functools
import json
import re
from typing import List, Set, Dict, Generator

from nltk.stem import PorterStemmer

from boolparser import bool_expr_ast


class Analyzer:
    """Filtering stopwords and stemming"""

    def __init__(self, stopwords=None):
        if stopwords is None:
            self.stopwords = []
        else:
            self.stopwords = stopwords
        self.ps = PorterStemmer()

    def get_terms(self, stream) -> Generator[str, None, None]:
        """Takes in a stream of words and returns a list of terms."""
        words = filter(None, re.split(r'[^a-z0-9]', stream.lower()))
        for word in words:
            if word not in self.stopwords:
                stemmed_word = self.ps.stem(word)
                if stemmed_word:
                    yield stemmed_word


class Index:
    """Collection parsing and index construction"""

    def __init__(self, stopwords):
        self.stopwords = stopwords
        self.analyzer = Analyzer(self.stopwords)
        # TODO (Issue #4): Should the inverted index be a dictionary, or its own class?
        self.title_index = dict()
        self.inverted_index = dict()  # We'll encode the index as a nested dictionary

    def parse(self, collection_fp: str) -> None:
        """Parses the collection file to construct the internal
        index structure (stored as the attribute self._index)
        """
        with open(collection_fp) as f:
            # TODO: What if the file won't fit in memory? (We can ignore this for now)
            content: str = f.read()
        for page in self._parse_xml(content):
            stream = page['stream']
            terms = self.analyzer.get_terms(stream)

            self.title_index[page['id']] = page['title']
            # Start adding entries to the inverted index
            for pos, term in enumerate(terms):
                if term in self.inverted_index:
                    if page['id'] in self.inverted_index[term]:
                        self.inverted_index[term][page['id']].append(pos)
                    else:
                        self.inverted_index[term][page['id']] = [pos]
                else:
                    self.inverted_index[term] = {}
                    self.inverted_index[term][page['id']] = [pos]

    def _parse_xml(self, s) -> Generator[Dict, None, None]:
        # TODO: If we use a different data dump, we should use a library like lxml
        while s.find('<page>') > -1:
            start_i = s.find('<id>')
            end_i = s.find('</id>')
            doc_id = s[start_i + 4:end_i]

            start_i = s.find('<title>')
            end_i = s.find('</title')
            title = s[start_i + 7: end_i]

            start_i = s.find('<text>')
            end_i = s.find('</text>')
            text = s[start_i + 6: end_i]
            stream = '{}\n{}'.format(title, text)

            yield {'id': doc_id, 'title': title, 'stream': stream}
            s = s[s.find('</page>') + 1:]

    def read(self, index_filepath: str, title_filepath: str) -> None:
        """Constructs the index from the input index file at
        the given path."""
        # self._index = ...
        with open(index_filepath, 'r') as f:
            self.inverted_index = json.load(f)
        with open(title_filepath, 'r') as f:
            self.title_index = json.load(f)

    def write(self, index_filepath: str, title_filepath: str) -> None:
        """Writes the index to disk at the given folder"""
        with open(index_filepath, 'w') as f:
            json.dump(self.inverted_index, f)
        with open(title_filepath, 'w') as f:
            json.dump(self.title_index, f)

    def search(self, query_string: str) -> List[int]:
        """Searches the index for the file"""
        query = QueryFactory.create(query_string)
        return sorted(query.match(self), key=int)
        # TODO (ISSUE 5): TF-IDF ranking
        # Scorer().score(results) ...

    def __getitem__(self, term) -> Dict[int, List[int]]:
        """Returns a dictionary containing mappings of doc_id to the
        positions in the document the term appears in.

        Documents in which the term doesn't appear in are not keys
        of the dictionary.
        """
        if term in self.inverted_index:
            return self.inverted_index[term]
        return dict()


class Query:
    def __init__(self, query_string: str):
        self.query_string = query_string

    def match(self, index: Index) -> Set[int]:
        """Returns the document IDs which match the given query
        """
        raise NotImplementedError


class OneWordQuery(Query):
    def match(self, index: Index) -> Set[int]:
        terms = index.analyzer.get_terms(self.query_string)
        # A single word may be split into multiple terms!
        # TODO: This doesn't match the spec. Should we update the spec?
        matches = [set(index[term].keys()) for term in terms]
        return functools.reduce(lambda s, t: s.union(t), matches)


class FreeTextQuery(OneWordQuery):
    pass


class PhraseQuery(Query):
    def match(self, index: Index) -> Set[int]:
        # TODO (Issue #3)
        query_terms = index.analyzer.get_terms(self.query_string)
        curr_indices = index[query_terms[0]]
        for i in range(1, len(query_terms)):
            next_indices = index[query_terms[i]]
            temp_next = dict()
            matches = set(curr_indices.keys()).intersection(set(next_indices.keys()))
            for doc_id in matches:
                doc_id_list = self.merge_lists(curr_indices[doc_id], next_indices[doc_id])
                if len(doc_id_list) > 0:
                    temp_next[doc_id] = doc_id_list
            curr_indices = temp_next
        return set(curr_indices.keys())

    def merge_lists(self, curr_indices: List, next_indices: List) -> List:
        to_return = []
        for i in range(len(curr_indices)):
            for j in range(len(next_indices)):
                if curr_indices[i] + 1 == next_indices[j]:
                    to_return.append(next_indices[j])
        return to_return


class BooleanQuery(Query):
    def match(self, index: Index) -> Set[int]:
        # TODO (Issue #2)
        #terms = index.analyzer.get_terms(self.query_string)
        # A single word may be split into multiple terms!
        parsed_query = bool_expr_ast(self.query_string)

        return self.helper(parsed_query, index)

    def helper(self, parsed_query, index):
        if isinstance(parsed_query, str):
            return OneWordQuery(parsed_query).match(index)

        operator, operands = parsed_query

        matches = [self.helper(operand, index) for operand in operands]
        if operator == 'OR':
            return functools.reduce(lambda s, t: s.union(t), matches)
        else:  # AND
            return functools.reduce(lambda s, t: s.intersection(t), matches)


class WildcardQuery(Query):
    def match(self, index: Index) -> Set[int]:
        # TODO (Issue #1)
        raise NotImplementedError


class QueryFactory:
    @staticmethod
    def create(query_string: str) -> Query:
        if query_string[0] == '"' and query_string[-1] == '"':
            return PhraseQuery(query_string)
        if any([t in query_string for t in ('(', ')', 'AND', 'OR')]):
            return BooleanQuery(query_string)
        words = query_string.split()
        if len(words) == 1:
            return OneWordQuery(query_string)
        elif len(words) > 1:
            return FreeTextQuery(query_string)
        else:
            raise ValueError('This query string is not supported.')


class Scorer:
    # TODO (Issue 5): TF-IDF ranking
    pass


def main():
    with open('data/part1/stopWords.dat') as f:
        test_stopwords = [line.rstrip('\n') for line in f]
    test_index = Index(test_stopwords)
    print('Loading Index')
    # Uncomment this call to read and comment the call to parse to read
    # test_index.read('testIndex.dat', 'testTitles.dat')
    test_index.parse('data/part1/testCollection.dat')
    print('Index Loaded')
    print('Saving index')
    test_index.write('testIndex.dat', 'testTitles.dat')
    print('Index Saved')
    print('Searching Index')
    with open('data/part1/testQueries.dat') as query_file:
        with open('data/part1/testExpected.dat') as result_file:
            for query, result in zip(query_file, result_file):
                print(query.rstrip('\n'))
                try:
                    print('Actual:', ' '.join(test_index.search(query.rstrip('\n'))))
                    print('Expected:', result.rstrip('\n'))
                except NotImplementedError:
                    print('Not implemented yet!')

if __name__ == '__main__':
    main()
