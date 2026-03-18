'''
Adapted for Gemini Vertex AI
'''
import argparse
import pandas
import time
from google import genai
from google.genai import types

def create_prompt(tuple1, tuple2, predicate):
    parts = []
    parts += [f'Is the following true ("Yes"/"No"): {predicate}?']
    parts += [f'Text 1: {tuple1}']
    parts += [f'Text 2: {tuple2}']
    parts += ['Answer:']
    return '\n'.join(parts)

def tuple_join(client, df1, df2, predicate, model):
    nr_pairs = len(df1) * len(df2)
    pair_counter = 0    
    results = []
    stats = []    
    
    # Configure strict 1-token output with thinking disabled
    config = types.GenerateContentConfig(
        max_output_tokens=1,
        temperature=0.0,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
    
    for _, row1 in df1.iterrows():
        for _, row2 in df2.iterrows():
            pair_counter += 1
            print(f'\nConsidering tuple pair {pair_counter}/{nr_pairs} ...')

            start_s = time.time()
            tuple1 = row1['text']
            tuple2 = row2['text']
            prompt = create_prompt(tuple1, tuple2, predicate)
            print(f'Prompt:\n---\n{prompt}\n---')
            
            # response = client.models.generate_content(
            #     model=model,
            #     contents=prompt
            #     # config=config
            # )
            
            # answer = response.text.strip() if response.text else ""

            response = None
            while True:
                try:
                    # Try to call the API
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                        # config=config
                    )
                    break # If it succeeds, break out of this while loop and continue!
                    
                except Exception as e:
                    error_msg = str(e)
                    # Check if the error is a rate limit (429)
                    if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                        print(f"⚠️ Quota exhausted! Pausing for 60 seconds to let the rate limit reset...")
                        time.sleep(60)
                    # Also catch 503 Server Unavailable errors just in case
                    elif '503' in error_msg:
                        print(f"⚠️ Google servers busy. Pausing for 30 seconds...")
                        time.sleep(30)
                    # If it's some other random error, print it and skip this pair
                    else:
                        print(f"❌ Unhandled Error: {e}")
                        break
            
            # Safely extract the answer (checking if response exists in case of unhandled errors)
            answer = response.text.strip() if response and response.text else ""
            print(f'Answer: {answer}')
            if answer == 'Yes':
                results += [{'tuple1':tuple1, 'tuple2':tuple2}]
            
            # Extract token usage from Gemini's metadata
            if response.usage_metadata:
                tokens_read = response.usage_metadata.prompt_token_count
                tokens_written = response.usage_metadata.candidates_token_count
            else:
                tokens_read = 0
                tokens_written = 0
                
            total_s = time.time() - start_s
            
            stats += [
                {'tokens_read':tokens_read, 
                 'tokens_written':tokens_written,
                 'seconds':total_s}]
            
            # Throttle to avoid hitting Google Cloud's RPM rate limits on large datasets
            # time.sleep(1.5)
    
    return stats, results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project_id', type=str, help='GCP Project ID')
    parser.add_argument('location', type=str, help='GCP Location (e.g. us-central1)')
    parser.add_argument('model', type=str, help='Name of Gemini model')
    parser.add_argument('input1', type=str, help='Path to .csv file')
    parser.add_argument('input2', type=str, help='Path to .csv file')
    parser.add_argument('predicate', type=str, help='Join predicate')
    parser.add_argument('stats_out', type=str, help='Path for statistics')
    parser.add_argument('result_out', type=str, help='Path for result')
    args = parser.parse_args()
    
    client = genai.Client(vertexai=True, project=args.project_id, location=args.location)
    
    df1 = pandas.read_csv(args.input1)
    df2 = pandas.read_csv(args.input2)
    
    statistics, result = tuple_join(client, df1, df2, args.predicate, args.model)
    statistics = pandas.DataFrame(statistics)
    result = pandas.DataFrame(result)
    statistics.to_csv(args.stats_out)
    result.to_csv(args.result_out)