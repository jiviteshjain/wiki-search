# %%
import xml.sax
from datetime import datetime
import config as conf
import os
import shutil
from nltk.stem.snowball import SnowballStemmer
import re
# %%
class TextProcessor:

    STOPWORDS = set(['whence', 'here', 'show', 'were', 'why', 'nt', 'the', 'whereupon', 'not', 'more', 'how', 'eight', 'indeed', 'i', 'only', 'via', 'nine', 're', 'themselves', 'almost', 'to', 'already', 'front', 'least', 'becomes', 'thereby', 'doing', 'her', 'together', 'be', 'often', 'then', 'quite', 'less', 'many', 'they', 'ourselves', 'take', 'its', 'yours', 'each', 'would', 'may', 'namely', 'do', 'whose', 'whether', 'side', 'both', 'what', 'between', 'toward', 'our', 'whereby', "'m", 'formerly', 'myself', 'had', 'really', 'call', 'keep', "'re", 'hereupon', 'can', 'their', 'eleven', '’m', 'even', 'around', 'twenty', 'mostly', 'did', 'at', 'an', 'seems', 'serious', 'against', "n't", 'except', 'has', 'five', 'he', 'last', '‘ve', 'because', 'we', 'himself', 'yet', 'something', 'somehow', '‘m', 'towards', 'his', 'six', 'anywhere', 'us', '‘d', 'thru', 'thus', 'which', 'everything', 'become', 'herein', 'one', 'in', 'although', 'sometime', 'give', 'cannot', 'besides', 'across', 'noone', 'ever', 'that', 'over', 'among', 'during', 'however', 'when', 'sometimes', 'still', 'seemed', 'get', "'ve", 'him', 'with', 'part', 'beyond', 'everyone', 'same', 'this', 'latterly', 'no', 'regarding', 'elsewhere', 'others', 'moreover', 'else', 'back', 'alone', 'somewhere', 'are', 'will', 'beforehand', 'ten', 'very', 'most', 'three', 'former', '’re', 'otherwise', 'several', 'also', 'whatever', 'am', 'becoming', 'beside', '’s', 'nothing', 'some', 'since', 'thence', 'anyway', 'out', 'up', 'well', 'it', 'various', 'four', 'top', '‘s', 'than', 'under', 'might', 'could', 'by', 'too', 'and', 'whom', '‘ll', 'say', 'therefore', "'s", 'other', 'throughout', 'became', 'your', 'put', 'per', "'ll", 'fifteen', 'must', 'before', 'whenever', 'anyone', 'without', 'does', 'was', 'where', 'thereafter', "'d", 'another', 'yourselves', 'n‘t', 'see', 'go', 'wherever', 'just', 'seeming', 'hence', 'full', 'whereafter', 'bottom', 'whole', 'own', 'empty', 'due', 'behind', 'while', 'onto', 'wherein', 'off', 'again', 'a', 'two', 'above', 'therein', 'sixty', 'those', 'whereas', 'using', 'latter', 'used', 'my', 'herself', 'hers', 'or', 'neither', 'forty', 'thereupon', 'now', 'after', 'yourself', 'whither', 'rather', 'once', 'from', 'until', 'anything', 'few', 'into', 'such', 'being', 'make', 'mine', 'please', 'along', 'hundred', 'should', 'below', 'third', 'unless', 'upon', 'perhaps', 'ours', 'but', 'never', 'whoever', 'fifty', 'any', 'all', 'nobody', 'there', 'have', 'anyhow', 'of', 'seem', 'down', 'is', 'every', '’ll', 'much', 'none', 'further', 'me', 'who', 'nevertheless', 'about', 'everywhere', 'name', 'enough', '’d', 'next', 'meanwhile', 'though', 'through', 'on', 'first', 'been', 'hereby', 'if', 'move', 'so', 'either', 'amongst', 'for', 'twelve', 'nor', 'she', 'always', 'these', 'as', '’ve', 'amount', '‘re', 'someone', 'afterwards', 'you', 'nowhere', 'itself', 'done', 'hereafter', 'within', 'made', 'ca', 'them'])

    def __init__(self):
        self._word_stems = {}
        self._stemmer = SnowballStemmer(language='english')
        self._tokenizer_regex = re.compile(r'[^a-z0-9]+')  # Call after case folding.
        self._category_regex = re.compile(r'\[\[Category:(.*)\]\]', flags=re.DOTALL)
        self._infobox_regex = re.compile(r'\{\{Infobox', flags=re.DOTALL)
        self._references_regex = re.compile(r'&lt;ref[^/]*?&gt;(.*?)&lt;/ref&gt;', flags=re.DOTALL)

    def _IsUsefulWord(self, word):
        return ((word not in self.STOPWORDS) and
                (word.isalnum()) and  # Removes punctuation, which is
                                         # also removed by the current regex.
                (len(word) >= conf.MIN_INDEXED_WORD_LENGTH) and
                (len(word) <= conf.MAX_INDEXED_WORD_LENGTH) and
                (not word.isnumeric()))  # Removes standalone numbers.

    def Clean(self, text):
        # TODO: Count total number of words somewhere here.
        words = [w for w in self._tokenizer_regex.split(text.casefold()) if self._IsUsefulWord(w)]
        tokens = []
        for word in words:
            if word not in self._word_stems:
                stem = self._stemmer.stem(word)
                tokens.append(stem)
                self._word_stems[word] = stem
            else:
                tokens.append(self._word_stems[word])

        return tokens

    def GetRegex(self):
        return self._infobox_regex, self._references_regex, self._category_regex


class Article:
    def __init__(self, id, title, body):
        self._id = id
        self._title = title
        self._body = body

    def _AddToIndex(self, index, tokens, type):
        for token in tokens:
            if token not in index:
                index[token] = [0, 0, 0, 0, 0, 0]
            
            index[token][type] += 1

        return index
    # For every token use a list instead of dictionary to simplify and
    # hasten access.
    # Order: [title, infobox, body, category, links, references]
    def Index(self, text_processor):
        # Clean the title.
        cleaned_title = text_processor.Clean(self._title)

        # Segregate the body.
        infobox_regex, references_regex, category_regex = text_processor.GetRegex()
        
        # Get the infobox out.
        infobox_matches = list(infobox_regex.finditer(self._body))
        if len(infobox_matches) > 0:
            last_match_end = infobox_matches[-1].end()
            candidate_string = self._body[last_match_end : last_match_end + conf.MAX_ESTIMATED_INFOBOX_LENGTH + 1]
            infobox_end = last_match_end
            
            candidate_lines = candidate_string.split('\n')
            if len(candidate_lines) > 0:
                infobox_end += (len(candidate_lines[0]) + 1)
                for line in candidate_lines[1:]:  # Skip the first line, as it does not begin with pipe
                    if line.strip().startswith('|'):
                        infobox_end += (len(line) + 1)  # +1 for the '\n'
                    else:
                        break

            cleaned_infobox = text_processor.Clean(self._body[:infobox_end + 1])
            self._body = self._body[infobox_end:]
        else:
            cleaned_infobox = []

        # Get the references out.
        references = references_regex.findall(self._body)
        self._body = references_regex.sub(' ', self._body)
        cleaned_references = text_processor.Clean(' '.join(references))

        # Get the categories out.
        for category_match in category_regex.finditer(self._body):  # Avoid finding all matches.
            cleaned_category = text_processor.Clean(self._body[category_match.start():])
            self._body = self._body[:category_match.start()]
            break
        else:
            cleaned_category = []

        # Get the links out.
        lower_body = self._body.casefold()
        split = lower_body.split('==external links==')
        if len(split) == 1:
            split = lower_body.split('==external links ==')
        if len(split) == 1:
            split = lower_body.split('== external links==')
        if len(split) == 1:
            split = lower_body.split('== external links ==')
        
        if len(split) > 1:
            cleaned_links = text_processor.Clean(split[-1])
            cleaned_body = text_processor.Clean(split[0])  # Already lowercase.
        else:
            cleaned_links = []
            cleaned_body = text_processor.Clean(self._body)

        # Create the index
        index = {}
        index = self._AddToIndex(index, cleaned_title, 0)
        index = self._AddToIndex(index, cleaned_infobox, 1)
        index = self._AddToIndex(index, cleaned_body, 2)
        index = self._AddToIndex(index, cleaned_category, 3)
        index = self._AddToIndex(index, cleaned_links, 4)
        index = self._AddToIndex(index, cleaned_references, 5)

        return index

    def Id(self):
        return self._id

    def Title(self):
        return self._title


class InvertedIndex:
    def __init__(self, text_processor):
        self._index = {}
        self._article_count = 0
        self._text_processor = text_processor

    def _PostingListToString(self, article_id, posting):
        posting_str = 'd' + str(article_id)
        if posting[0] > 0:
            posting_str += ('t' + str(posting[0]))
        if posting[1] > 0:
            posting_str += ('i' + str(posting[1]))
        if posting[2] > 0:
            posting_str += ('b' + str(posting[2]))
        if posting[3] > 0:
            posting_str += ('c' + str(posting[3]))
        if posting[4] > 0:
            posting_str += ('l' + str(posting[4]))
        if posting[5] > 0:
            posting_str += ('r' + str(posting[5]))
        return posting_str

    def AddArticle(self, article):
        article_index = article.Index(self._text_processor)
        for token, posting in article_index.items():
            if not token in self._index:
                self._index[token] = ''

            # posting_string = f'd{article.Id()}t{posting[0]}i{posting[1]}b{posting[2]}c{posting[3]}l{posting[4]}r{posting[5]}'
            posting_string = self._PostingListToString(article.Id(), posting)
            self._index[token] += posting_string

        self._article_count += 1

    def ArticleCount(self):
        return self._article_count

    def Clear(self):
        self._index = {}
        self._article_count = 0

    def Get(self):
        return self._index


class IntermediateFileHandler:
    def __init__(self, path):
        self._path = path
        self._file_count = 0

    def WriteFile(self, inverted_index):
        if len(inverted_index) == 0:
            return

        tokens = sorted(inverted_index.keys())

        with open(os.path.join(self._path, conf.INTERMED_DIR, f'{self._file_count}.txt'),
                  'w', conf.INTERMED_FILE_WRITE_BUFFER) as f:
            for token in tokens:
                f.write(f'{token}:{inverted_index[token]}\n')

        self._file_count += 1

# Non-processed strings are written here, as the output is user-facing.
class TitleHandler:
    def __init__(self, path):
        self._path = path
        self._titles = []

    def AddTitle(self, title):
        self._titles.append(title.strip())

    def WriteFile(self):
        with open(os.path.join(self._path, conf.TITLES_FILE), 'w') as f:
            for title in self._titles:
                f.write(title + '\n')

# Implementating of xml.sax's ContentHandler, which contains callbacks
# for tag events that occur while parsing the Wikipedia XML.
class ParsingHandler(xml.sax.ContentHandler):
    def __init__(self, inverted_index, intermed_file_handler, title_handler):
        super().__init__()
        self._tag = ''
        self._article_id = 0
        self._title = ''
        self._text = ''

        self._inverted_index = inverted_index
        self._intermed_file_handler = intermed_file_handler
        self._title_handler = title_handler

    def startElement(self, name, attrs):
        self._tag = name

    def characters(self, content):
        # Only store the content if the current tag is <title> or <text>.
        # These tags only appear within a <page> tag.
        if self._tag == 'title':
            self._title += content
        elif self._tag == 'text':
            self._text += content

    def endElement(self, name):
        # Because the content of other tags is processed on the fly as
        # new characters are discovered, the only tag that needs to be
        # handled at the end is the <page> tag.
        if name == 'page':
            # Order of articles in the title handler is important. This
            # should not be performed in workers.
            self._title_handler.AddTitle(self._title)

            article = Article(self._article_id, self._title, self._text)
            # Adding the article to the inverted index calls Article.Parse(),
            # which parses and indexes the individual article and can be
            # delegated to workers.
            self._inverted_index.AddArticle(article)
            
            self._article_id += 1
            self._title = ''
            self._text = ''

            # Reached enough articles to write in a separate file.
            if self._inverted_index.ArticleCount() == conf.ARTICLES_PER_INTERMED_FILE:
                self._intermed_file_handler.WriteFile(self._inverted_index.Get())
                self._inverted_index.Clear()

        # Write the articles left over at the end.
        elif name == 'mediawiki':
            if self._inverted_index.ArticleCount() > 0:
                self._intermed_file_handler.WriteFile(self._inverted_index.Get())
                self._inverted_index.Clear()

    
def parse(data_path, index_path):
    shutil.rmtree(index_path, ignore_errors=True)
    os.makedirs(os.path.join(index_path, conf.INTERMED_DIR))

    text_processor = TextProcessor()
    inverted_index = InvertedIndex(text_processor)
    intermed_file_handler = IntermediateFileHandler(index_path)
    title_handler = TitleHandler(index_path)
    
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = ParsingHandler(inverted_index, intermed_file_handler, title_handler)
    parser.setContentHandler(handler)

    start_time = datetime.now()
    
    for file in os.listdir(data_path):
        parser.parse(os.path.join(data_path, file))
    
    title_handler.WriteFile()
    
    end_time = datetime.now()
    return end_time - start_time

    


# %%
parse('../data/', '../index/')