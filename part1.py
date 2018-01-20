import re
import json
import functools
import os.path

from nltk.stem import PorterStemmer

import boolparser


class Analyzer(object):
    """Class for turning a stream into terms."""

    def __init__(self, stopwords=None):
        if stopwords is None:
            self.stopwords = []
        else:
            self.stopwords = stopwords
        self.ps = PorterStemmer()

    def terms(self, stream):
        """Takes in a stream of words and returns a list of terms."""
        # TODO: Option to preserve parentheses
        words = filter(None, re.split(r'[^a-zA-Z0-9]', stream.lower()))
        terms = []
        for word in words:
            if word not in self.stopwords:
                try:
                    stemmed_word = self.ps.stem(word)
                    if stemmed_word:
                        terms.append(stemmed_word)
                except:
                    print(word, 'could not be stemmed')
        return terms


class Index(object):
    # TODO: Use Apache Lucene as guidance
    # https://lucene.apache.org/core/3_0_3/fileformats.html#file-names
    # We must support:
    # - Term frequencies
    # - Term positions

    def __init__(self,
                 stopword_path=None,
                 collection_path=None,
                 index_path='index.dat',
                 titles_path='titles.dat'):
        self.stopwords = []
        if stopword_path is not None:
            with open(stopword_path) as f:
                for line in f:
                    self.stopwords.append(line.rstrip('\n'))
        self.index_path = index_path
        self.titles_path = titles_path
        if collection_path is not None:
            self.create_index(collection_path)
        self.index = self.load_index()

    def create_index(self, collection_path):
        """Creates the inverted index and title index from the
        given collection file.
        """
        assert not os.path.exists(self.index_path)
        assert not os.path.exists(self.titles_path)
        with open(collection_path) as f:
            s = f.read()
        self.parse(s)
        self.invert()

    def parse(self, s):
        analyzer = Analyzer(self.stopwords)
        for i, page in enumerate(self.parse_xml(s)):
            print('Indexing doc {}'.format(i))
            stream = page['stream']
            terms = analyzer.terms(stream)
            with open(self.titles_path, 'a') as title_file:
                json.dump({'id': page['id'], 'title': page['title']},
                          title_file)
                title_file.write('\n')
            with open(self.index_path, 'a') as index_file:
                for pos, term in enumerate(terms):
                    json.dump({'term': term, 'id': page['id'], 'pos': pos},
                              index_file)
                    index_file.write('\n')
            print('Indexed doc {}'.format(i))

    def parse_xml(self, s):
        while s.find('<page>') > 0:
            start_i = s.find('<id>')
            end_i = s.find('</id>')
            id = int(s[start_i + 4:end_i])

            start_i = s.find('<title>')
            end_i = s.find('</title')
            title = s[start_i + 7: end_i]

            start_i = s.find('<text>')
            end_i = s.find('</text>')
            text = s[start_i + 6: end_i]
            stream = '{}\n{}'.format(title, text)

            yield {'id': id, 'title': title, 'stream': stream}
            s = s[s.find('</page>') + 1:]  # Go to the next page

    def invert(self):
        index = []
        with open(self.index_path) as index_file:
            for line in index_file:
                term_obj = json.loads(line)
                index.append(term_obj)
        index.sort(key=lambda x: x['term'])
        with open(self.index_path, 'w') as index_file:
            for obj in index:
                index_file.write('{}\n'.format(json.dumps(obj)))

    def load_index(self):
        """Reads the inverted index into a Python dictionary.
        The keys are terms and the values are lists of ids.
        """
        raise NotImplementedError

    def query(self, qs: str):
        """Searches the inverted index given a query string.
        """
        query = QueryFactory.create(qs, index)
        return sorted(query.get_matches())


class Query(object):
    def __init__(self, query_string: str, index: Index):
        self.query_terms = Analyzer(stopwords=index.stopwords).terms(query_string)
        self.index = index

    def get_matches(self):
        """Returns the set of IDs in the index corresponding to the query."""
        raise NotImplementedError


class OneWordQuery(Query):
    def is_match(self, term) -> bool:
        return self.query_terms[0] == term

    def get_matches(self) -> set:
        matches = []
        with open(self.index.index_path) as f:
            for line in f:
                term_obj = json.loads(line)
                if self.is_match(term_obj['term']):
                    matches.append(term_obj['id'])
        return set(matches)


class FreeTextQuery(Query):
    def get_matches(self):
        matches = set()
        for qt in self.query_terms:
            matches |= OneWordQuery(qt, self.index).get_matches()
        return matches


class PhraseQuery(Query):
    def __init__(self, query_string: str, index: Index):
        without_quotes = query_string[1:-1]
        super(PhraseQuery, self).__init__(without_quotes, index)

    def get_matches(self):
        # track of document position
        raise NotImplementedError


class BooleanQuery(Query):
    def __init__(self, query_string: str, index: Index):
        self.query_ast = boolparser.bool_expr_ast(query_string)
        self.analyzer = Analyzer(stopwords=index.stopwords)
        super(BooleanQuery, self).__init__(query_string, index)

    def get_matches(self):
        return self._get_matches(self.query_ast)

    def _get_matches(self, ast):
        if isinstance(ast, str):
            return OneWordQuery(ast, self.index).get_matches()
        if isinstance(ast, tuple):
            operator, operands = ast
            if operator == 'OR':
                unjoined_matches = [self._get_matches(el) for el in operands]
                return functools.reduce(lambda x, y: x | y, unjoined_matches)
            elif operator == 'AND':
                unjoined_matches = [self._get_matches(el) for el in operands]
                return functools.reduce(lambda x, y: x & y, unjoined_matches)


class QueryFactory(object):
    """Creates and parses the query string"""

    @staticmethod
    def create(qs, index):
        if qs[0] == '"' and qs[-1] == '"':
            return PhraseQuery(qs, index)
        if 'AND' in qs or 'OR' in qs:
            return BooleanQuery(qs, index)
        words = qs.split(' ')
        if len(words) == 1:
            return OneWordQuery(qs, index)
        elif len(words) > 1:
            return FreeTextQuery(qs, index)
        else:
            raise ValueError('The query string given is not supported.')


if __name__ == '__main__':
    # index = Index(stopword_path='data/part1/stopWords.dat',
    #               collection_path='data/part1/testCollection.dat',
    #               index_path='testIndex.dat',
    #               titles_path='testTitles.dat')
    index = Index(index_path='testIndex.dat',
                  titles_path='testTitles.dat')
    print(index.query('(password OR secret) AND (login OR account)'))
    # with open('data/part1/testQueries.dat') as f:
    #     for line in f:
    #         print(line.rstrip('\n'))
    #         print(index.query(line.rstrip('\n')))
