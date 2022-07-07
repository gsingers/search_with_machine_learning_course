import pandas as pd
import csv
from sklearn.utils import shuffle

# Read input file
pdf = pd.read_csv("/workspace/datasets/fasttext/labeled_products.txt"
                    , header=None, sep="__",quotechar='\0'
                    ).drop(columns=[0,1])

# Split input
pdf = pdf[2].str.split(" ",1,expand=True)

# Name columns
pdf.columns = ['cat_code', 'prod_desc']

# Set minimum product count for a category
min_cnt = 500

# Count products and Subset for min prod count per category
pdf_cnt = pdf.groupby('cat_code')['prod_desc'].count().reset_index(name='cnt1').sort_values('cnt1', ascending=False)
pdf_cnt = pdf_cnt[pdf_cnt.cnt1 >= min_cnt]

# Merge with main dataset
pdf_new = pdf.merge(pdf_cnt, on='cat_code').drop(columns='cnt1')
pdf_new['output'] = "__label__"+pdf['cat_code'] +" "+ pdf['prod_desc']
pdf_new = shuffle(pdf_new)
print(pdf_new[['output']])

# output the pruned products
pdf_new[['output']].to_csv("/workspace/datasets/fasttext/pruned_labeled_products.txt"
                            ,index=False, header=False, quoting=csv.QUOTE_NONE, quotechar="",  escapechar="\\")


