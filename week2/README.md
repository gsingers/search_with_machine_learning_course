## Changes from Week 1

- A new `conf` folder for capturing project specific configurations. See `week2/conf`
- Added a new analyzer to better process tokens and mixed case product names (e.g. X-Men, iPad). See the  index settings and mappings in `week2/conf/bbuy_products.json`. 
  - The [char_group tokenizer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-chargroup-tokenizer.html) breaks text into terms whenever it encounters a character which is in a defined set. It is mostly useful for cases where a simple custom tokenization is desired, and the overhead of use of the pattern tokenizer is not acceptable.
  - [Word Delimiter Graph Token Filter](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-word-delimiter-graph-tokenfilter.html) - Splits tokens at non-alphanumeric characters. The word_delimiter_graph filter also performs optional token normalization based on a set of rules. By default, the filter uses the following rules:
    - Split tokens at non-alphanumeric characters. The filter uses these characters as delimiters. For example: Super-Duper → Super, Duper
    - Remove leading or trailing delimiters from each token. For example: XL---42+'Autocoder' → XL, 42, Autocoder
    - Split tokens at letter case transitions. For example: PowerShot → Power, Shot
    - Split tokens at letter-number transitions. For example: XL500 → XL, 500
    - Remove the English possessive ('s) from the end of each token. For example: Neil's → Neil
    
    
## Tricks

- Activate the specific environment. Install jupyter & jupyterlab `pip install jupyter jupyterlab`. `jupyter-lab --NotebookApp.allow_origin='*'`. Access the jupyterlab ui at `https:///8888-gitpod-url`