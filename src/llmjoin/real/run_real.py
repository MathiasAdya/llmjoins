'''
Created on Feb 25, 2024

@author: immanueltrummer
'''
import argparse
from llmjoin.real.adaptive_join import adaptive_join
from llmjoin.real.block_join import block_join
# from llmjoin.real.embedding_join import embedding_join
# from llmjoin.real.LOTUS_join import lotus_join
from llmjoin.real.tuple_join import tuple_join
# import openai
import pandas
from google import genai


def run_benchmark(client, df1, df2, predicate, scenario):
    """ Benchmark join algorithms in given scenario.
    
    Args:
        client: OpenAI client.
        df1: left join input.
        df2: right join input.
        predicate: join predicate.
        scenario: scenario name (used in names of output files).
    """
    named_ops = [
        # (adaptive_join, 'adaptive_join'), 
        # (block_join, 'block_join'),
        # (embedding_join, 'embedding_join'),
        # (lotus_join, 'lotus_join'),
        (tuple_join, 'tuple_join'),
        ]
        
    for join_op, op_name in named_ops:
        statistics, result = join_op(
            client, df1, df2, 
            predicate, model)
        
        statistics = pandas.DataFrame(statistics)
        result = pandas.DataFrame(result)
        statistics.to_csv(f'testresults/{op_name}_{scenario}_stats.csv')
        result.to_csv(f'testresults/{op_name}_{scenario}_results.csv')


if __name__ == '__main__':
    

    parser = argparse.ArgumentParser()
    parser.add_argument('project_id', type=str, help='GCP Project ID')
    parser.add_argument('location', type=str, help='GCP Location (e.g. us-central1)')
    args = parser.parse_args()

    # parser = argparse.ArgumentParser()
    # parser.add_argument('ai_key', type=str, help='OpenAI access key')
    # args = parser.parse_args()
    
    # client = openai.OpenAI(api_key=args.ai_key, timeout=300)
    # model = 'gpt-4'
    # model = 'gpt-4.1-mini'


    client = genai.Client(vertexai=True, project=args.project_id, location=args.location)
    model = 'gemini-2.5-flash'
    
    # ads = pandas.read_csv('testdata/ads.csv')
    # searches = pandas.read_csv('testdata/searches.csv')
    # predicate = 'the search matches the offer precisely'
    # run_benchmark(client, ads, searches, predicate, 'ad_matches_search')
    # print('Ran ad_matches')
    #
    reviews_1 = pandas.read_csv('testdata/reviews_1.csv')
    reviews_2 = pandas.read_csv('testdata/reviews_2.csv')
    predicate = 'both reviews are positive or both are negative'
    run_benchmark(client, reviews_1, reviews_2, predicate, 'same_reviews')
    print('Ran same_review')
    #
    # emails = pandas.read_csv('testdata/emails.csv')
    # statements = pandas.read_csv('testdata/statements.csv')
    # predicate = 'The two texts contradict each other'
    # run_benchmark(client, statements, emails, predicate, 'inconsistencies')
    # print('Ran inconsistency')
    
    # sentences_1 = pandas.read_csv('testdata/sentences_1.csv')
    # sentences_2 = pandas.read_csv('testdata/sentences_2.csv')
    # predicate = 'The first sentence entails the second sentence'
    # run_benchmark(client, sentences_1, sentences_2, predicate, 'entailment')
    # print('Ran entailment')
    
    # predicate = 'The first sentence contradicts the second sentence'
    # run_benchmark(client, sentences_1, sentences_2, predicate, 'contradiction')
    # print('Ran contradiction')
    
    # words_1 = pandas.read_csv('testdata/words_1.csv')
    # words_2 = pandas.read_csv('testdata/words_2.csv')
    # predicate = 'The two words start with the same letter'
    # run_benchmark(client, words_1, words_2, predicate, 'words')
    # print('Ran words')
    
    # for nr_names in [
    #     # 50,
    #     100,
    #     # 150,
    #     # 200,
    #     # 250 
    #     ]:
    #     emails = pandas.read_csv(f'testdata/emails{nr_names}names.csv')
    #     statements = pandas.read_csv(f'testdata/statements{nr_names}names.csv')
    #     predicate = 'The two texts contradict each other'
    #     scenario = f'inconsistency{nr_names}names'
    #     run_benchmark(client, statements, emails, predicate, scenario)