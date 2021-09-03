# wiki-search
An indexing and search engine for English Wikipedia.

## Phase 1

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