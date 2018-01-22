from typing import List

import pytest

from core import Index


@pytest.fixture
def small_index() -> Index:
    # TODO: Consider using the pytest fixture decorator
    index = Index([])
    index.parse('data/part1/small.dat')
    return index


def test_one_word_query(small_index):
    assert small_index.search('2001') == ['0', '3']
    assert small_index.search('first') == ['1', '2']


def test_free_text_query(small_index):
    assert small_index.search('first 2001') == ['0', '1', '2', '3']
    assert small_index.search('2001 first') == ['0', '1', '2', '3']


def test_boolean_query(small_index):
    assert small_index.search('2001 OR first') == ['0', '1', '2', '3']
    assert small_index.search('2001 AND first') == []


