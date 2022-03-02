#!/usr/bin/env bash

set -x

MODEL_NAME="$1"
SOURCE_FILE="/workspace/datasets/fasttext/$MODEL_NAME"
TRAIN_FILE="$SOURCE_FILE.train"
TEST_FILE="$SOURCE_FILE.test"
MODEL="$SOURCE_FILE.model"
SPLIT="10000"

echo "Cleaning"
[ -f "$TRAIN_FILE" ] && rm "$TRAIN_FILE"
[ -f "$TEST_FILE" ] && rm "$TEST_FILE"

echo "Creating train/test files"
shuf "$SOURCE_FILE" | head -$SPLIT > "$TRAIN_FILE"
shuf "$SOURCE_FILE" | tail -$SPLIT > "$TEST_FILE"

LR="1.0"
EPOCH="25"
NGRAMS="2"
echo "Training..."
fasttext supervised -input "$TRAIN_FILE" -output "$MODEL" -lr "$LR" -epoch "$EPOCH" -wordNgrams "$NGRAMS"

echo "Testing..."
fasttext test "$MODEL.bin" "$TEST_FILE"

echo "Done."
