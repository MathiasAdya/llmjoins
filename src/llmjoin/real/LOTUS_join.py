'''
Created on Oct 8, 2025

@author: immanueltrummer
'''
import argparse
import openai
import pandas
import time
import lotus
from lotus.models import LM


def lotus_join(client, df1, df2, predicate, model):
    """ Perform join using the LOTUS system.
    
    Args:
        client: OpenAI client.
        df1: first input table.
        df2: second input table.
        predicate: join predicate.
        model: name of OpenAI model.
    
    Returns:
        Tuple: statistics, join result.
    """
    lm = LM(model=model)
    lotus.settings.configure(lm=lm)    
    # Rename column to 'text' in df1 to 'text1'
    df1 = df1.rename(columns={'text': 'text1'})
    # Rename column to 'text' in df2 to 'text2'
    df2 = df2.rename(columns={'text': 'text2'})
    # Perform semantic join in LOTUS
    start_s = time.time()
    result_df = df1.sem_join(
        df2, "'{text1}', '{text2}':" + predicate)
    virtual_usage = lm.__dict__['stats'].virtual_usage
    tokens_read = virtual_usage.prompt_tokens
    tokens_written = virtual_usage.completion_tokens
    total_s = time.time() - start_s
    # Iterate over rows of result_df
    results = []    
    for _, row in result_df.iterrows():
        row_pair = {
            'tuple1': row['text1'], 
            'tuple2': row['text2']}
        results.append(row_pair)
    
    stats = [
        {'tokens_read':tokens_read, 
         'tokens_written':tokens_written,
         'seconds':total_s}]
    
    return stats, results


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('ai_key', type=str, help='Key for OpenAI access')
    parser.add_argument('model', type=str, help='Name of OpenAI model')
    parser.add_argument('input1', type=str, help='Path to .csv file')
    parser.add_argument('input2', type=str, help='Path to .csv file')
    parser.add_argument('predicate', type=str, help='Join predicate')
    parser.add_argument('stats_out', type=str, help='Path for statistics')
    parser.add_argument('result_out', type=str, help='Path for result')
    args = parser.parse_args()
    
    # client = openai.OpenAI(api_key=args.ai_key, timeout=10)
    df1 = pandas.read_csv(args.input1)
    df2 = pandas.read_csv(args.input2)
    
    statistics, result = lotus_join(
        None, df1, df2, 
        args.predicate, args.model)
    statistics = pandas.DataFrame(statistics)
    result = pandas.DataFrame(result)
    statistics.to_csv(args.stats_out)
    result.to_csv(args.result_out)