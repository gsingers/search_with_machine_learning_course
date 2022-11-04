import logging
import warnings
import pandas as pd
import fasttext
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings('ignore')

def read_df(input_path:str) -> pd.DataFrame:
    df = pd.read_csv(input_path, names=['word'])
    return df

def load_model(model_path:str) -> fasttext.FastText._FastText:
    model = fasttext.load_model(model_path)
    return model

def get_synonyms(model:fasttext.FastText._FastText, word:str, k:int=5) -> list:
    synonyms = model.get_nearest_neighbors(word)
    return synonyms


def get_synonyms_from_df(
    df:pd.DataFrame,
    model:fasttext.FastText._FastText,
    min_similarity:float
) -> pd.DataFrame:
    synonyms_df = pd.DataFrame(columns=['word', 'synonym', 'similarity'])
    for word in df['word']:
        synonyms = get_synonyms(model, word)
        for synonym in synonyms:
            synonyms_df = synonyms_df.append({'word': word, 'synonym': synonym[1], 'similarity': synonym[0]}, ignore_index=True)
    return synonyms_df[synonyms_df['similarity'] > min_similarity]


input_path = '/workspace/datasets/fasttext/top_words.txt'
model_path = '/workspace/datasets/fasttext/title_model_3.bin'
output_path = '/workspace/datasets/fasttext/synonyms.csv'
min_similarity = 0.8

if __name__ == '__main__':
    logging.info(f'Loading data from {input_path}...')
    data_df = read_df(input_path)
    logging.info(f'Loading model from {model_path}...')
    model = load_model(model_path)
    logging.info(f'Generating synonyms...')
    synonyms_df = get_synonyms_from_df(data_df, model, min_similarity)
    logging.info(f'Saving DataFrame to {output_path}...')
    synonyms_df.to_csv(output_path, index=False, header=False)
    logging.info(f'Synonyms saved to {output_path}.')
