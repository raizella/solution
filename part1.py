import re
import json

from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer


class Index(object):
    def __init__(self, stopword_path, collection_path, index_path, titles_path):
        # TODO: There should be an option to just load an
        # already constructed index
        self.stopwords = []
        with open(stopword_path) as f:
            for line in f:
                self.stopwords.append(line.rstrip('\n'))
        with open(collection_path) as f:
            s = f.read()  # TODO: What if the file is too large
            collection = BeautifulSoup(s, 'lxml')
        self.ps = PorterStemmer()
        self.index_path = index_path
        self.titles_path = titles_path
        for page in collection.find_all('page'):
            id = page.find('id').text
            title = page.find('title').text
            text = page.find('text').text
            words = re.split(r'[^a-zA-Z]', text.lower())
            terms = []
            for word in words:
                if word not in self.stopwords:
                    try:
                        stemmed_word = self.ps.stem(word)
                    except:
                        print(word, 'could not be stemmed')
                        stemmed_word = word
                    if stemmed_word:
                        terms.append(stemmed_word)
            with open(self.titles_path, 'a') as title_file:
                json.dump({'id': id, 'title': title}, title_file)
                title_file.write('\n')
            with open(self.index_path, 'a') as index_file:
                for pos, term in enumerate(terms):
                    json.dump({'term': term, 'id': id, 'pos': pos}, index_file)
                    index_file.write('\n')

    def query(self, qs: str):
        query = QueryFactory.create(qs)
        index = []
        with open(self.index_path) as f:
            for line in f:
                index.append(json.loads(line))
        return query.matches(index)


class Query(object):
    def __init__(self, qs):
        self.qs = qs
        self.ps = PorterStemmer()

    def matches(self, index):
        raise NotImplementedError


class OneWordQuery(Query):
    def is_match(self, term) -> bool:
        return self.ps.stem(self.qs) == term

    def matches(self, index):
        matches = []
        for term_obj in index:
            if self.is_match(term_obj['term']):
                matches.append(term_obj['id'])
        return matches


class FreeTextQuery(Query):
    def is_match(self, term):
        for word in self.qs.split():
            if self.ps.stem(word) == term:
                return True
        return False

    def matches(self, index):
        matches = []
        for term_obj in index:
            if self.is_match(term_obj['term']):
                matches.append(term_obj['id'])
        return matches


class PhraseQuery(Query):
    def __init__(self, qs):
        super(PhraseQuery, self).__init__(qs[1:-1]) # Ignore quote chars

    def is_match(self, index, start_i):
        for offset, word in enumerate(self.qs.split()):
            if (start_i + offset < len(index)
                    and self.ps.stem(word) != index[start_i + offset]):
                return False
            # TODO: This does not ensure that the terms are in the same document
        return True

    def matches(self, index):
        # TODO: The qs quotations need to be filtered.
        matches = []
        for i, term_obj in enumerate(index):
            if self.is_match(index, i):
                matches.append(term_obj['id'])
        return matches


class BooleanQuery(Query):
    def match(self, doc):
        # TODO: Parse out the parentheses and AND/OR operators
        # TODO: Complete the operations as a bunch of union/intersection operations
        pass

    def matches(self, index):
        raise NotImplementedError


class QueryFactory(object):
    @staticmethod
    def create(qs):
        if qs[0] == '"' and qs[-1] == '"':
            return PhraseQuery(qs)
        if 'AND' in qs or 'OR' in qs:
            return BooleanQuery(qs)
        words = qs.split(' ')
        if len(words) == 1:
            return OneWordQuery(qs)
        elif len(words) > 1:
            return FreeTextQuery(qs)
        else:
            raise ValueError('The query string cannot be parsed.')


if __name__ == '__main__':
    index = Index('data/part1/stopWords.dat',
          'data/part1/testCollection.dat',
          'testIndex.dat',
          'testTitles.dat')
    with open('data/part1/testQueries.dat') as f:
        for line in f:
            print(index.query(line.rstrip('\n')))
