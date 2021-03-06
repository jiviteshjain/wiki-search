# Indexing
ARTICLES_PER_INTERMED_FILE = 10000
INTERMED_DIR = 'intermed'
INTERMED_FILE_WRITE_BUFFER = -1

TOKENS_PER_FINAL_FILE = 10000
INTERMED_FILE_READ_BUFFER = -1
TITLES_DIR = 'titles'
TITLES_PER_FILE = 200000
FIRST_WORD_FILE = 'heads.txt'

MAX_INDEXED_WORD_LENGTH = 43
MIN_INDEXED_WORD_LENGTH = 2
MAX_INDEXED_NUM_LENGTH = 4
ALPHANUM_SAFE_THRESH = 13
ALPHANUM_UNSAFE_NUM_THRESH = 4

MAX_ESTIMATED_INFOBOX_LENGTH = 1000

ENCODING_BASE = 36

# Search
# WEIGHT_TITLE = 100
# WEIGHT_INFOBOX = 20
# WEIGHT_BODY = 1 #10
# WEIGHT_CATEGORY = 10 #3
# WEIGHT_LINKS = 0.01
# WEIGHT_REFERENCES = 0.03  # TODO: Should this be higher than links?
# WEIGHT_REQUESTED_FIELD = 10000

WEIGHT_TITLE = 1000
WEIGHT_INFOBOX = 10
WEIGHT_BODY = 5 #10
WEIGHT_CATEGORY = 2 #3
WEIGHT_LINKS = 0.5
WEIGHT_REFERENCES = 0.1  # TODO: Should this be higher than links?
WEIGHT_REQUESTED_FIELD = 10000

NUM_ARTICLES = (21384756 - 1312010)
NUM_RESULTS = 10
STRICTLY_RETURN_NUM_RESULTS = True
NUM_SEARCH_WORKERS = 8
