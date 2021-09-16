from parse import Parse
from merge import Merge
from search import Search
from argparse import ArgumentParser
from datetime import datetime
import subprocess
import os

def SearchMain(index_path, queries_file, results_file):
    if (queries_file is None) or (results_file is None):
        raise ValueError('--queries and --results are necessary for searching.')
    
    queries = []
    with open(queries_file, 'r') as f:
        for line in f:
            queries.append(line.strip())

    search_results, run_times = Search(index_path, queries)

    with open(results_file, 'w') as f:
        for result, time in zip(search_results, run_times):
            for article_id, article_title in result:
                f.write(f'{article_id}, {article_title}\n')
            f.write(f'{time}\n\n')
    

def IndexMain(dump_path, index_path, stats_path):
    if (dump_path is None) or (stats_path is None):
        raise ValueError('--dump and --stats are necessary for indexing.')
    
    begin_time = datetime.now()
    
    print('Creating intermediate index.')
    Parse(dump_path, index_path)
    print('Merging index.')
    indexed_count = Merge(index_path)
    
    end_time = datetime.now()

    index_size = int(subprocess.check_output(['du', '-sg', index_path]).decode('utf-8').split()[0])

    file_count = len(os.listdir(index_path)) - 2

    with open(stats_path, 'w') as f:
        f.write(f'{index_size}\n{file_count}\n{indexed_count}\n')

    print(f'Done in {end_time - begin_time}.')




if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--action', type=str, choices=('index', 'search'), required=True)

    parser.add_argument('--dump', type=str, required=False, help='Path to Wikipedia dump. Only necessary when action is index.')
    parser.add_argument('--stats', type=str, required=False, help='Path to statistics file. Only necessary when action is index.')

    parser.add_argument('--index', type=str, required=True, help='Path to inverted index.')

    parser.add_argument('--queries', type=str, required=False, help='Path to queries file. Only necessary when action is search.')

    parser.add_argument('--results', type=str, required=False, help='Path to results file. Only necessary when action is search.')

    args = parser.parse_args()

    if args.action == 'index':
        IndexMain(args.dump, args.index, args.stats)
    else:
        SearchMain(args.index, args.queries, args.results)