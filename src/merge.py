from io import FileIO
import os
import heapq
import config as conf
import sys
from datetime import datetime

class HeapNode:
    def __init__(self, word, posting_list, file_id):
        self._word = word
        self._posting_list = posting_list
        self._file_id = file_id

    def Word(self):
        return self._word

    def PostingList(self):
        return self._posting_list
    
    def FileId(self):
        return self._file_id

    def __lt__(self, other):
        if self._word != other.Word():
            return self._word < other.Word()

        return self._file_id < other.FileId()

class FinalFileHandler:
    def __init__(self, path):
        self._path = path
        self._file_count = 0
        self._heads = []
        self._lines = []
        self._word_count = 0
        

    def AddLine(self, word, posting_list):
        if len(self._lines) == 0:
            self._heads.append(word)

        line = word + ':' + posting_list
        self._lines.append(line)
        self._word_count += 1

        if len(self._lines) >= conf.TOKENS_PER_FINAL_FILE:
            with open(os.path.join(self._path, f'{self._file_count}.txt'), 'w') as f:
                for line in self._lines:
                    f.write(line + '\n')
            
            self._file_count += 1
            self._lines = []

    def Close(self):
        if len(self._lines) >= 0:
            with open(os.path.join(self._path, f'{self._file_count}.txt'), 'w') as f:
                for line in self._lines:
                    f.write(line + '\n')
            
            self._file_count += 1
            self._lines = []

        if len(self._heads) > 0:
            with open(os.path.join(self._path, conf.FIRST_WORD_FILE), 'w') as f:
                for line in self._heads:
                    f.write(line + '\n')

            self._heads = []

        return self._word_count

class IntermediatePageHandler:
    def __init__(self, path):
        self._path = os.path.join(path, conf.INTERMED_DIR)
        
        self._files = []
        for file in os.listdir(self._path):
            try:
                f = open(os.path.join(self._path, file), 'r', conf.INTERMED_FILE_READ_BUFFER)
                self._files.append(f)
            except IOError:
                print(f'Failed to open intermediate file: {file}. Skipping.', file=sys.stderr)

        self._eofs = set()

    def __len__(self):
        return len(self._files)

    def ReadLine(self, file_id):
        if file_id in self._eofs:
            return None

        try:
            line = self._files[file_id].readline().strip()
        except IOError:
            print(f'Failed to read from intermediate file: {file_id}. Skipping.', file=sys.stderr)
            self._eofs.add(file_id)
            return None
        
        if len(line) == 0:
            self._eofs.add(file_id)
            return None

        word, posting_list = line.split(':')
        return HeapNode(word, posting_list, file_id)

    def Close(self):
        for f in self._files:
            try:
                f.close()
            except IOError:
                print(f'Failed to close an intermediate file. Skipping.', file=sys.stderr)
                pass


def merge(path):

    start_time = datetime.now()

    intermed_handler = IntermediatePageHandler(path)
    
    heap = [intermed_handler.ReadLine(i) for i in range(len(intermed_handler))]
    heapq.heapify(heap)

    final_handler = FinalFileHandler(path)

    current_word = ''
    current_posting_list = ''
    while len(heap) > 0:
        next_node = heap[0]
        heapq.heappop(heap)

        if next_node.Word() == current_word:
            current_posting_list += next_node.PostingList()
        else:
            if len(current_posting_list) > 0:
                final_handler.AddLine(current_word, current_posting_list)
            
            current_word = next_node.Word()
            current_posting_list = next_node.PostingList()

        new_node = intermed_handler.ReadLine(next_node.FileId())
        if new_node is not None:
            heapq.heappush(heap, new_node)

    if len(current_posting_list) > 0:
        final_handler.AddLine(current_word, current_posting_list)

    word_count = final_handler.Close()
    intermed_handler.Close()

    end_time = datetime.now()

    return (end_time - start_time), word_count
    
print(merge('../index/'))