#!/bin/bash
get_seeded_random()
{
  seed="$1"
  echo $seed
  openssl enc -aes-256-ctr -pass pass:"$seed" -nosalt \
    </dev/zero 2>/dev/null
}

cat /workspace/datasets/fasttext/labeled_queries.txt |shuf --output=/workspace/datasets/fasttext/shuf_labeled_queries.txt --random-source=<(get_seeded_random $1) 