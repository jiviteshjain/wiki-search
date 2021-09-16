# %%
import os
import matplotlib.pyplot as plt
from tqdm.auto import tqdm as tq
import numpy as np

char_counts = []
doc_counts = []
alphanumerics = []
long_words = []
THRESH = 100000
# %%
path = '../index2/'
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
            if len(word) > 7 and word.isalnum() and (not word.isalpha()) and (not word.isnumeric()):
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
