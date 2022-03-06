# We’ll use a small portion of text data extracted from English
# Wikipedia (50,000 random lines), which we’ve placed in
# /workspace/data/search_with_machine_learning/wiki_sample.txt.

~/fastText-0.9.2/fasttext skipgram -input /workspace/search_with_machine_learning/data/wiki_sample.txt -output wiki -maxn 0

# The fastText library comes with a nearest-neighbor method that
# we can use to obtain synonyms. Try words like "politics" or "linux".

~/fastText-0.9.2/fasttext nn wiki.bin
