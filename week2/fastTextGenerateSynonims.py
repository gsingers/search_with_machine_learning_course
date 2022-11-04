import pandas as pd
import fasttext

def read_df(input_path:str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    return df

def load_model(model_path:str) -> fasttext.FastText._FastText:
    model = fasttext.load_model(model_path)
    return model

def get_synonyms(model:fasttext.FastText._FastText, word:str, k:int=5) -> list:
    synonyms = model.get_nearest_neighbors(word)
    return synonyms


def get_synonyms_from_df(df:pd.DataFrame, model:fasttext.FastText._FastText) -> pd.DataFrame:
    synonyms_df = pd.DataFrame(columns=['word', 'synonym', 'similarity'])
    for word in df['word']:
        synonyms = get_synonyms(model, word)
        for synonym in synonyms:
            synonyms_df = synonyms_df.append({'word': word, 'synonym': synonym[0], 'similarity': synonym[1]}, ignore_index=True)
    return synonyms_df


input_path = '/workspace/datasets/fasttext/top_words.txt'
model_path = './title_model_3.bin'
output_path = '/workspace/datasets/fasttext/synonyms.txt'

if __name__ == '__main__':
    data_df = read_df(input_path)
    model = load_model(model_path)
    synonyms_df = get_synonyms_from_df(data_df, model)
    synonyms_df.to_csv(output_path, index=False)
