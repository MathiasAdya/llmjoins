'''
Created on Feb 27, 2024

@author: immanueltrummer
'''
from argparse import ArgumentParser
from llmjoin.real.analyze import analyze_stats
from llmjoin.real.analyze import analyze_results
from pandas import read_csv
from pathlib import Path

import pandas as pd


if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('dir', type=str, help='Path to result directory')
    args = parser.parse_args()
    
    op_names = [
        'tuple_join', 
        # 'block_join', 
        # 'adaptive_join', 
        # 'embedding_join', 
        # 'lotus_join'
    ]
    scenarios = [
            ('inconsistencies', 'inconsistencies.csv'),
            # ('inconsistency50names', 'inconsistencies50names.csv'),
            # ('inconsistency100names', 'inconsistencies100names.csv'),
            # ('inconsistency150names', 'inconsistencies150names.csv'),
            # ('inconsistency200names', 'inconsistencies200names.csv'),
            # ('inconsistency250names', 'inconsistencies250names.csv'),
            ('same_reviews', 'same_reviews.csv'),
            # ('ad_matches', 'ad_matches_search.csv'),
            # ('entailment', 'entailment_gt.csv'),
            # ('contradiction', 'contradiction_gt.csv'),
            # ('words', 'words_join.csv')
    ]
        
    
    all_aggregates = []
    for op_name in op_names:
        for scenario, ref_name in scenarios:
            print(f'*** {scenario} - {op_name} ***')
            
            prefix = f'{op_name}_{scenario}_'
            ref_path = Path('testdata') / ref_name
            results_dir = Path(args.dir)
            result_path = results_dir / f'{prefix}results.csv'
            stats_path = results_dir / f'{prefix}stats.csv'
            
            if not result_path.exists() or not stats_path.exists():
                print('At least one file does not exist:')
                print(result_path)
                print(stats_path)
                continue
            
            reference = read_csv(str(ref_path))
            results = read_csv(str(result_path))
            stats = read_csv(str(stats_path))
            
            quality_aggs = analyze_results(reference, results)
            cost_aggs = analyze_stats(stats)
            all_aggregates.append({
                'scenario': scenario,
                'op_name': op_name,
                **quality_aggs,
                **cost_aggs
                })

    all_aggs_df = pd.DataFrame(all_aggregates)
    
    for metric in [
        'cents', 'tokens_read', 
        'tokens_written', 'seconds',
        'precision', 'recall', 'f1_score']:
        for op_name in op_names:
            op_aggs = all_aggs_df[all_aggs_df['op_name'] == op_name]
            agg_vals = op_aggs[metric].tolist()
            avg_val = sum(agg_vals)/len(agg_vals)
            agg_vals += [avg_val]
            plot_code = '\\addplot coordinates {'
            for idx, value in enumerate(agg_vals, 1):
                plot_code += f'({idx},{value}) '
            plot_code += '};'
            print(f'% {op_name} - {metric} - avg: {avg_val}')
            print(plot_code)