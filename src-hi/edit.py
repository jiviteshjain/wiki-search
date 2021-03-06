# %%
import os
from tqdm.auto import tqdm as tq
from search import Searcher
import config as conf
from parse import Encode

# %%
src_path = '../index-final/'
dst_path = '../index-final-truncated/'
os.makedirs(dst_path)
THRESH = 500000

def PostingListToString(posting):
    posting_str = 'd' + Encode(posting['d'])
    if posting['t'] > 0:
        posting_str += ('t' + Encode(posting['t']))
    if posting['i'] > 0:
        posting_str += ('i' + Encode(posting['i']))
    if posting['b'] > 0:
        posting_str += ('b' + Encode(posting['b']))
    if posting['c'] > 0:
        posting_str += ('c' + Encode(posting['c']))
    if posting['l'] > 0:
        posting_str += ('l' + Encode(posting['l']))
    if posting['r'] > 0:
        posting_str += ('r' + Encode(posting['r']))
    return posting_str

pbar = tq(os.listdir(src_path))
edited_lines = 0
for file in pbar:
    if file in ('heads.txt', 'titles'):
        continue
    with open(os.path.join(src_path, file), 'r') as f:
        with open(os.path.join(dst_path, file), 'w') as f2:
            for line in f:
                word, posting_string = line.strip().split(':')
                posting_list = posting_string.split('d')[1:]

                if len(posting_list) > THRESH:
                    edited_lines += 1
                    pbar.set_postfix({'Edited lines': edited_lines})
                    parsed_posting_list = [Searcher.ParsePosting(p) for p in posting_list]
                    for posting in parsed_posting_list:
                        posting['score'] = ((conf.WEIGHT_TITLE * posting['t']) + \
                                            (conf.WEIGHT_INFOBOX * posting['i']) + \
                                            (conf.WEIGHT_BODY * posting['b']) + \
                                            (conf.WEIGHT_CATEGORY * posting['c']) + \
                                            (conf.WEIGHT_LINKS * posting['l']) + \
                                            (conf.WEIGHT_REFERENCES * posting['r']))
                    parsed_posting_list.sort(key=lambda x: x['score'], reverse=True)
                    parsed_posting_list = parsed_posting_list[:THRESH]
                    posting_string = ''
                    for p in parsed_posting_list:
                        posting_string += PostingListToString(p)
                
                f2.write(word + ':' + posting_string + '\n')

print('COPY HEADS AND TITLES')
# %%
