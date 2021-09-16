# %%
import os
import config as conf
from bisect import bisect_right
from parse import TextProcessor
import linecache
from multiprocessing import Pool
from itertools import repeat
import math
from random import randrange
from datetime import datetime, timedelta

class IndexHeadsManager:
    def __init__(self, path):
        with open(os.path.join(path, conf.FIRST_WORD_FILE), 'r') as f:
            self._heads = [h.strip() for h in f.readlines()]

    # UNUSED
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

    def GetFile(self, key):
        # From Python's documentation of bisect. Returns the rightmost
        # element less than or equal to key.
        # Returns -1 if not found.
        return bisect_right(self._heads, key) - 1


class TitleManager:
    def __init__(self, path):
        self._path = os.path.join(path, conf.TITLES_DIR)
    
    def GetTitle(self, article_id):
        file_id = article_id // conf.TITLES_PER_FILE
        line_num = (article_id % conf.TITLES_PER_FILE) + 1

        # Returns empty string on error.
        return linecache.getline(os.path.join(self._path, f'{file_id}.txt'), line_num).strip().lower()


# UNUSED
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
    parsed_posting_list = [Searcher._ParsePosting(p) for p in posting_list]

    for doc in parsed_posting_list:
        for field in doc.keys():
            if field != 'd':
                search_results[field].append(doc['d'])

    return search_results

def ProcessPostingString(posting_string, fields, num_docs):
    posting = Searcher.ParsePosting(posting_string)
    tf = ((conf.WEIGHT_TITLE * posting['t']) + \
          (conf.WEIGHT_INFOBOX * posting['i']) + \
          (conf.WEIGHT_BODY * posting['b']) + \
          (conf.WEIGHT_CATEGORY * posting['c']) + \
          (conf.WEIGHT_LINKS * posting['l']) + \
          (conf.WEIGHT_REFERENCES * posting['r']))
    
    # Only in case of field queries, increase the weights of those fields.
    for field in fields:
        if field != 'a':
            tf += (conf.WEIGHT_REQUESTED_FIELD * posting[field])

    idf = conf.NUM_ARTICLES / num_docs

    return posting['d'], math.log10(tf) * math.log10(idf)


class Searcher:
    def __init__(self, path, text_processor, index_heads, titles, pool):
        self._path = path
        self._text_processor = text_processor
        self._index_heads = index_heads
        self._titles = titles
        self._pool = pool

    @classmethod
    def _ParseQueryFields(cls, query):
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

    @classmethod
    def ParsePosting(cls, posting):
        parsed_posting = {}
        
        field = 'd'
        cur = ''
        
        for c in posting:
            if c.isalpha():
                parsed_posting[field] = int(cur, base=conf.ENCODING_BASE)
                field = c
                cur = ''
            else:
                cur += c
        
        if len(cur) > 0:
            parsed_posting[field] = int(cur, base=conf.ENCODING_BASE)

        # Set empty fields to 0.
        for field in ('t', 'i', 'b', 'c', 'l', 'r'):  # 'd' is guaranteed to be present.
            if field not in parsed_posting:
                parsed_posting[field] = 0

        return parsed_posting

    def _SearchToken(self, token, fields):
        file_id = self._index_heads.GetFile(token)
        if file_id < 0:
            return {}

        with open(os.path.join(self._path, f'{file_id}.txt'), 'r') as f:
            for line in f:
                word, posting_string = line.strip().split(':')  # Gauranteed to have ':' and
                                                                # non empty parts on both sides.
                if word == token:
                    break
            else:
                return {}

        posting_list = posting_string.split('d')[1:]  # Gauranteed to start with 'd' and be non-empty.
                                                      # Skip the empty string in the beginning.
        
        search_results = self._pool.starmap(ProcessPostingString,
                                            zip(posting_list, repeat(fields), repeat(len(posting_list))))

        return search_results

    def Search(self, query):
        query_fields = self._ParseQueryFields(query)
        
        # Invert the query fields, storing for every token, the field(s)
        # in which it is desired.
        query_tokens = {}
        
        for field, field_string in query_fields.items():
            field_tokens = self._text_processor.Clean(field_string)
            for token in field_tokens:
                if token not in query_tokens:
                    query_tokens[token] = [field, ]
                else:
                    query_tokens[token].append(field)

        token_matches = [self._SearchToken(*x) for x in zip(query_tokens.keys(),
                                               query_tokens.values())]

        # Aggregate results across terms, by adding the scores.
        scored_matches = {}
        for token_match in token_matches:
            for article_id, tfidf in token_match:
                if article_id in scored_matches:
                    scored_matches[article_id] += tfidf
                else:
                    scored_matches[article_id] = tfidf

        # Sort the results.
        search_results = sorted(scored_matches.keys(), reverse=True,
                                key=lambda x: scored_matches[x])

        if conf.STRICTLY_RETURN_NUM_RESULTS:
            while len(search_results) < conf.NUM_RESULTS:
                random_article_id = randrange(conf.NUM_ARTICLES)
                if random_article_id not in search_results:
                    search_results.append(random_article_id)

        entitled_search_results = [(r, self._titles.GetTitle(r)) 
                                    for r in search_results[:conf.NUM_RESULTS]]

        return entitled_search_results

# %%
def Search(index_path, queries):
    text_processor = TextProcessor()
    index_heads = IndexHeadsManager(index_path)
    titles = TitleManager(index_path)
    pool = Pool(conf.NUM_SEARCH_WORKERS)
    searcher = Searcher(index_path, text_processor, index_heads, titles, pool)

    search_results = []
    run_times = []

    for query in queries:
        begin = datetime.now()
        search_results.append(searcher.Search(query))
        end = datetime.now()
        delta = end - begin
        run_times.append(delta / timedelta(seconds=1))
    
    pool.close()
    pool.join()

    return search_results, run_times
# %%
