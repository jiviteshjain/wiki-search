# %%
import os
import matplotlib.pyplot as plt
from tqdm.auto import tqdm as tq
import numpy as np
from pprint import pprint
import linecache
from search import TitleManager

char_counts = []
doc_counts = []
alphanumerics = []
long_words = []
THRESH = 100000
# %%
path = '../index-small/'
for file in tq(os.listdir(path)):
    if file in ('heads.txt', 'titles'):
        continue
    with open(os.path.join(path, file), 'r') as f:
        for line in f:
            word, posting_string = line.strip().split(':')
            char_counts.append(len(posting_string))
            doc_counts.append(len(posting_string.split('d')) - 1)
            if doc_counts[-1] > THRESH:
                long_words.append((word, doc_counts[-1]))
            word = word.strip()
            if word.isalnum() and (not word.isalpha()) and (not word.isnumeric()):
                alphanumerics.append(word)
# %%
print(alphanumerics)

# %%
big_doc_counts = [x for x in doc_counts if x > 100000]

# %%
plt.hist(big_doc_counts, bins=100)
# plt.hist(doc_counts, range=(0, 2000), bins=250)
fg = plt.gcf()
fg.set_size_inches(12, 6)
plt.show()
# %%
with open('../analysis/long-words.txt', 'w') as f:
    for word, count in long_words:
        f.write(str(count) + ', ' + word + '\n')
# %%
line = linecache.getline('../index2/2806.txt', 5137)
# %%
posting_string = line.strip().split(':')[1]
# %%
posting_list = posting_string.split('d')[1:]
# %%
def ParsePosting(posting):
    parsed_posting = {}
    
    field = 'd'
    cur = ''
    
    for c in posting:
        if c.isalpha() and c.islower():
            parsed_posting[field] = int(cur, base=10)
            field = c
            cur = ''
        else:
            cur += c
    
    if len(cur) > 0:
        parsed_posting[field] = int(cur, base=10)

    # Set empty fields to 0.
    for field in ('t', 'i', 'b', 'c', 'l', 'r'):  # 'd' is guaranteed to be present.
        if field not in parsed_posting:
            parsed_posting[field] = 0

    return parsed_posting

parsed_posting_list = [ParsePosting(p) for p in posting_list]
# %%
