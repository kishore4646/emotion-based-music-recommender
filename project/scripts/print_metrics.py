import pandas as pd
import os
p = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset.csv')
p = os.path.normpath(p)
if not os.path.exists(p):
    print('MISSING', p)
else:
    df = pd.read_csv(p)
    df['text_length'] = df['text'].str.split().apply(len)
    print('rows', len(df))
    print('total_words', int(df['text_length'].sum()))
    print('avg', float(df['text_length'].mean()))
    print('unique_texts', int(df['text'].nunique()))
