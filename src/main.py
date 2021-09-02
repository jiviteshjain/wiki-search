from parse import Parse
from merge import Merge
from search import Search
from argparse import ArgumentParser
import json
from datetime import datetime

def SearchMain(index_path, query):
    if query is None:
        raise ValueError('--query is necessary for searching.')
    
    search_results = Search(index_path, query)
    json_string = json.dumps(search_results, indent=2)
    print(json_string)
    

def IndexMain(dump_path, index_path, stats_path):
    if (dump_path is None) or (stats_path is None):
        raise ValueError('--dump and --stats are necessary for indexing.')
    
    begin_time = datetime.now()
    
    print('Creating intermediate index.')
    Parse(dump_path, index_path)
    print('Merging index.')
    Merge(index_path)
    
    end_time = datetime.now()
    time_delta = end_time - begin_time
    print(f'Done in {time_delta.seconds} s.')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--action', type=str, choices=('index', 'search'), required=True)

    parser.add_argument('--dump', type=str, required=False, help='Path to Wikipedia dump. Only necessary for when action is index.')
    parser.add_argument('--stats', type=str, required=False, help='Path to statistics file. Only necessary when action is index.')

    parser.add_argument('--index', type=str, required=True, help='Path to inverted index.')

    parser.add_argument('--query', type=str, required=False, help='Query string. Only necessary when action is search.')

    args = parser.parse_args()

    if args.action == 'index':
        IndexMain(args.dump, args.index, args.stats)
    else:
        SearchMain(args.index, args.query)