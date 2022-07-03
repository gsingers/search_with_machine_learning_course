import pandas as pd
import os

def filter():
    #dataset = pd.read_csv('/workspace/datasets/fasttext/training_data.txt', on_bad_lines='skip', delimiter='\t')
    #print(dataset.iloc[1])
    with open('/workspace/datasets/fasttext/training_data.txt', 'r') as f:
        index = 0
        dataset = pd.DataFrame(columns=['label', 'name'])
        for line in f:
            split = line.split(' ')
            label = split[0]
            name = " ".join(w for w in split[1:])

            dataset.loc[index] = pd.Series({'label': label, 'name': name})
            index +=1
    print(dataset.head())
    dataset.to_csv('dataset.csv')

def clean_dataset():
    dataset = pd.read_csv('dataset.csv')
    df2 = dataset.groupby(['label'])['label'].count()
    joined = dataset.set_index('label').join(df2)
    
    print(joined[joined['label']>50])
    print(df2[df2 > 50].shape)

    #print(len(dataset['label']))




if __name__ == "__main__":
    clean_dataset()
