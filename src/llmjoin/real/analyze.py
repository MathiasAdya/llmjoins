'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
import argparse
import pandas


def analyze_results(reference, results):
    """ Print result statistics after comparison to reference.
    
    Args:
        reference: data frame with reference results.
        results: results to evaluate.
    
    Returns:
        Dictionary with aggregate statistics on result quality.
    """
    ref_rows = reference[reference['joins']].copy()
    ref_rows['resultpair'] = ref_rows.apply(
        lambda r:(r['text1'], r['text2']), axis=1)
    ref_tuples = set(ref_rows['resultpair'])
    nr_refs = len(ref_tuples)
    
    #print(f'References: {ref_tuples}')
    
    nr_correct = 0
    nr_incorrect = 0
    for _, row in results.iterrows():
        result_tuple = (row['tuple1'], row['tuple2'])
        #print(result_tuple)
        if result_tuple in ref_tuples:
            #print('Correct!')
            nr_correct += 1
        else:
            #print('Incorrect!')
            nr_incorrect += 1
    
    nr_results = len(results)
    recall = nr_correct/nr_refs
    precision = nr_correct/nr_results
    f1_score = 0 if precision == 0 or recall == 0 else \
        2 * precision * recall / (precision+recall)
    
    print(f'Recall:   \t{recall}')
    print(f'Precision:\t{precision}')
    print(f'F1 Score: \t{f1_score}')
    
    return {
        'nr_refs': nr_refs,
        'nr_results': nr_results,
        'nr_correct': nr_correct,
        'nr_incorrect': nr_incorrect,
        'recall': recall,
        'precision': precision,
        'f1_score': f1_score
        }


def analyze_stats(stats):
    """ Print aggregate performance statistics.
    
    Args:
        stats: performance statistics.
    
    Returns:
        Dictionary with aggregate statistics on processing overheads.
    """
    seconds = stats['seconds'].sum()
    tokens_read = stats['tokens_read'].sum()
    tokens_written = stats['tokens_written'].sum()
    gpt4_USD = tokens_read * 0.03/1000 + tokens_written * 0.06/1000
    gpt41mini_USD = tokens_read * 0.4/1000000 + tokens_written * 1.6/1000000
    text3_USD = (tokens_read + tokens_written) * 0.02/1000000
    total_USD = gpt41mini_USD + text3_USD
    if 'overflow' in stats.columns:
        nr_prompts = len(stats[stats['overflow'] == False])
    else:
        nr_prompts = len(stats)
    
    print(f'Tokens read:   \t{tokens_read}')
    print(f'Tokens written:\t{tokens_written}')
    print(f'Seconds:       \t{seconds}')
    print(f'GPT-4 $:       \t{gpt4_USD}')
    print(f'Text-3 $:       \t{text3_USD}')
    print(f'#Prompts:      \t:{nr_prompts}')
    
    return {
        'tokens_read': tokens_read,
        'tokens_written': tokens_written,
        'seconds': seconds,
        'gpt4_USD': gpt4_USD,
        'gpt41mini_USD': gpt41mini_USD,
        'text3_USD': text3_USD,
        'nr_prompts': nr_prompts,
        'total_USD': total_USD,
        'cents': 100 * total_USD
        }


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('refpath', type=str, help='Path to reference result')
    parser.add_argument('resultpath', type=str, help='Path to join results')
    parser.add_argument('statspath', type=str, help='Path to input statistics')
    args = parser.parse_args()
    
    reference = pandas.read_csv(args.refpath)
    results = pandas.read_csv(args.resultpath)
    stats = pandas.read_csv(args.statspath)
    
    analyze_results(reference, results)
    analyze_stats(stats)