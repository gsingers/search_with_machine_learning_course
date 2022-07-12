OUTPUT_DIR=../workspace/datasets/week3_fasttext

MIN_QUERIES=1000
EPOCHS=25
LR=0.5
WORD_NGRAMS=1
STEM=True

DATA_SUFFIX=$(STEM)_$(MIN_QUERIES)
MODEL_SUFFIX=$(LR)_$(EPOCHS)_$(WORD_NGRAMS)_$(DATA_SUFFIX)


$(OUTPUT_DIR):
	mkdir -p $@

$(OUTPUT_DIR)/labeled_queries_$(DATA_SUFFIX).txt: $(OUTPUT_DIR)
	python ./create_labeled_queries.py --stem=$(STEM) --min_queries=$(MIN_QUERIES) --output /dev/stdout | shuf > $@


$(OUTPUT_DIR)/lq_training_$(DATA_SUFFIX).txt: $(OUTPUT_DIR)/labeled_queries_$(DATA_SUFFIX).txt
	head -n 50000 $< > $@

$(OUTPUT_DIR)/lq_test_$(DATA_SUFFIX).txt: $(OUTPUT_DIR)/labeled_queries_$(DATA_SUFFIX).txt
	tail -n 10000 $< > $@

$(OUTPUT_DIR)/lq_supervised_$(MODEL_SUFFIX).bin: $(OUTPUT_DIR)/lq_training_$(DATA_SUFFIX).txt
	fasttext supervised -input $< -output $(basename $@) -lr $(LR) -epoch $(EPOCHS) -wordNgrams $(WORD_NGRAMS)

label_counts: $(OUTPUT_DIR)/labeled_queries_$(DATA_SUFFIX).txt
		cat $< | cut -d ' ' -f 1 | sort | uniq -c | wc -l

test: $(OUTPUT_DIR)/lq_supervised_$(MODEL_SUFFIX).bin $(OUTPUT_DIR)/lq_test_$(DATA_SUFFIX).txt
	fasttext test $^ 1
	fasttext test $^ 2
	fasttext test $^ 3

clean:
	rm -rf $(OUTPUT_DIR)

.PHONY: test clean label_counts
.SECONDARY:
