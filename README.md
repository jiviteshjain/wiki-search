# wiki-search
An indexing and search engine for English Wikipedia.

## Running the phase 1 code

### Requirements

- `nltk`: Can be installed using `pip3 install nltk`

### Indexing

```shell
bash index.sh path/to/xml/dump path/to/index/folder path/to/statistics/file
```

### Searching

```shell
bash search.sh path/to/index/folder "query string"  # Query string must be quoted
```

## Running the phase 2 code

### Requirements

- `nltk`: Can be installed using `pip3 install nltk`
- `PyStemmer`: Can be installed using `pip3 install PyStemmer`

### Indexing

**English**  

```shell
bash index-en.sh path/to/xml/dump path/to/index/folder path/to/statistics/file
```
or
```shell
python3 src-en/main.py --action=index --dump=path/to/xml/dump --index=path/to/index/folder --stats=path/to/statistics/file
```

**Hindi**  

```shell
bash index-hi.sh path/to/xml/dump path/to/index/folder path/to/statistics/file
```
or
```shell
python3 src-hi/main.py --action=index --dump=path/to/xml/dump --index=path/to/index/folder --stats=path/to/statistics/file
```

### Searching

**English**  

```shell
bash search-en.sh path/to/index/folder path/to/queries/file path/to/results/file
```
or
```shell
python3 src-en/main.py --action=search --index=path/to/index/folder --queries=path/to/queries/file --results=path/to/results/file
```

**Hindi**  

```shell
bash search-hi.sh path/to/index/folder path/to/queries/file path/to/results/file
```
or
```shell
python3 src-hi/main.py --action=search --index=path/to/index/folder --queries=path/to/queries/file --results=path/to/results/file
```

## System description

This is a Wikipedia indexing and search engine, that uses the block merge algorithm to create and store an inverted index from a given Wikipedia XML dump. The inverted index can then be used to search for articles, with support for simple and field queries. Articles are ranked based on their term-frequency/inverse-document-frequency scores, weighted by the fields.

Fields supported for field queries are:
- Title (`t`)
- Infobox (`i`)
- Body (`b`)
- Categories (`c`)
- External Links (`l`)
- References (`r`)

### Indexing

As the XML dump is parsed, the extracted text is first tokenised, cleaned, and stemmed. Stopwords, and words that are a relic of the page's formatting are removed. An inverted index is created for a manageable chunk of articles at once, and then written to file, sorted by the tokens. Each article is given a unique ID, and the articles' titles are written to a separate set of files. The posting lists are designed to be space efficient, ignoring null values and using base 36 encoding instead of base 10.  
*(Code in `src-en/parse.py`)*  

These intermediate files only index a few articles each, and contain repeated tokens. Hence, they need to be merged into a (logically) single continuous index file, sorted by the tokens. This is achieved by merging the individual files together, using a heap - in a way akin to multi-way merge sort. In order to avoid the creation of a single large file which would be difficilt to traverse, this merged index file is written off to disk in chunks (with a fixed number of tokens in each). The first token of every file is written off to a separate file, which can be binary searched to determine the appropriate file to look for a word in, at search time.  
*(Code in `src-en/merge.py`)*  

### Searching

For every token in the tokenised and stemmed query, the aforementioned list of first tokens is binary searched to obtain the appropriate index file to look into. The index file is searched for a posting list corresponding to the token. This posting list is parsed (using multiple processes, for it can be long), and every article in which the token appears is given a weighted TF/IDF score, based on the weights of the individual fields. For field queries, the weights of the requested fields are significantly enhanced. These article-wise scores are aggregated across all tokens in the query, and the documents are sorted according to their final scores. The titles of these documents are read from the appropriate files, and returned to the user.  
*(Code in `src-en/search.py`)*

*(`src-en/config.py` contains configuration options, and `src-en/main.py` contains code for running the engine.)*  

### Hindi

The implementation for Hindi is almost identical to the one for English, except for the requisite differences in stemming, tokenization, stopword identification, and removal of non-useful tokens.  
The code organisation for Hindi is identical to that for English, with every file in `src-hi/` performing functions akin to its counterpart in `src-en/`.


