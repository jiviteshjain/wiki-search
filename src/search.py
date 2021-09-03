# %%
import os
import json
import config as conf
from bisect import bisect_right
from parse import TextProcessor

def ParseQueryFields(query):
    if ':' not in query:
        return {'a': query}

    query_fields = {}
    query_parts = query.strip().split(':')
    for i in range(1, len(query_parts)):
        field = query_parts[i-1][-1]
        
        field_string = query_parts[i]
        if i != len(query_parts)-1:
            field_string = field_string[:-1]

        if field in query_fields:
            query_fields[field] += (' ' + field_string)
        else:
            query_fields[field] = field_string

    return query_fields

class IndexHeadsManager:
    def __init__(self, path):
        with open(os.path.join(path, conf.FIRST_WORD_FILE), 'r') as f:
            self._heads = [h.strip() for h in f.readlines()]

    def _BinarySearch(self, key):
        low = 0
        high = len(self._heads) - 1
        
        while low <= high:
            mid = (low + high) // 2
            
            if self._heads[mid] == key:
                return mid
            
            elif self._heads[mid] < key:
                if mid < high and self._heads[mid + 1] <= key:
                    low = mid + 1
                else:
                    return mid

            else:
                high = mid - 1

        return -1

    def Search(self, key):
        # From Python's documentation of bisect. Returns the rightmost
        # element less than or equal to key.
        # Returns -1 if not found.
        return bisect_right(self._heads, key) - 1


def ParsePosting(posting):
    parsed_posting = {}
    
    field = 'd'
    cur = ''
    
    for c in posting:
        if c.isalpha():
            parsed_posting[field] = int(cur)
            field = c
            cur = ''
        else:
            cur += c
    
    if len(cur) > 0:
        parsed_posting[field] = int(cur)

    return parsed_posting

def FieldAgnosticSearch(token, index_heads, path):

    search_results = {
        't': [], 'i': [], 'b': [], 'c': [], 'l': [], 'r': []
    }

    file_id = index_heads.Search(token)
    
    if file_id < 0:
        return search_results

    with open(os.path.join(path, f'{file_id}.txt'), 'r') as f:
        for line in f:
            word, posting_string = line.strip().split(':')
            if word == token:
                break
        else:
            return search_results

    posting_list = posting_string.split('d')[1:]  # Gauranteed to start with 'd' and be non-empty.
                                                  # Skip the empty string in the beginning. 
    parsed_posting_list = [ParsePosting(p) for p in posting_list]

    for doc in parsed_posting_list:
        for field in doc.keys():
            if field != 'd':
                search_results[field].append(doc['d'])

    return search_results


def Search(path, query):
    text_processor = TextProcessor()
    index_heads = IndexHeadsManager(path)
    
    query_fields = ParseQueryFields(query)
    search_results = {}
    for query_string in query_fields.values():
        query_tokens = text_processor.FormatQuery(query_string)
        
        for token, stem in query_tokens.items():
            if stem is None:
                search_results[token] = {
                    'title': [],
                    'infobox': [],
                    'body': [],
                    'categories': [],
                    'links': [],
                    'references': []
                }
            else:
                out = FieldAgnosticSearch(stem, index_heads, path)
                search_results[token] = {
                    'title': out['t'],
                    'infobox': out['i'],
                    'body': out['b'],
                    'categories': out['c'],
                    'links': out['l'],
                    'references': out['r']
                }
    return search_results
