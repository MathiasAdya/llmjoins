'''
Created on Oct 16, 2025

@author: immanueltrummer

Generates statistics about a benchmark.

'''
import argparse
import pandas
import tiktoken

encoder = tiktoken.encoding_for_model('gpt-4o')


def avg_token_size(texts):
    """ Returns average token size of texts.
    
    Args:
        texts: list of texts.
    
    Returns:
        Average number of tokens used by GPT-4o tokenizer.
    """
    sizes = [len(encoder.encode(t)) for t in texts]
    return sum(sizes)/len(sizes)


def selectivity(truth_df):
    """ Compute selectivity of join in truth data frame.
    
    Args:
        truth_df: data frame with ground truth.
    
    Returns:
        Selectivity of join.
    """
    nr_positives = truth_df['joins'].sum()
    return nr_positives/len(truth_df)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'truth', type=str, 
        help='Path to ground truth CSV')
    args = parser.parse_args()
    
    truth_df = pandas.read_csv(args.truth)
    left_input = truth_df['text1'].unique()
    right_input = truth_df['text2'].unique()
    
    left_rows = len(left_input)
    right_rows = len(right_input)
    print(f'Left rows: {left_rows}')
    print(f'Right rows: {right_rows}')
    
    left_token_size = avg_token_size(left_input)
    right_token_size = avg_token_size(right_input)
    print(f'Avg. left input token size: {left_token_size}')
    print(f'Avg. right input token size: {right_token_size}')
    
    selectivity = selectivity(truth_df)
    print(f'Selectivity: {selectivity}')