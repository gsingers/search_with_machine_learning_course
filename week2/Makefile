OUTPUT_DIR=../workspace/datasets/fasttext

MIN_PRODUCTS=0
MAX_LABEL_DEPTH=99


$(OUTPUT_DIR)/%.fasttext:
	python ./createContentTrainingData.py --min_products=$(MIN_PRODUCTS) --max_label_depth=$(MAX_LABEL_DEPTH) --output /dev/stdout | shuf > $@


$(OUTPUT_DIR)/%_training.txt: $(OUTPUT_DIR)/%_shuffled.fasttext
	head -n 10000 $< > $@

$(OUTPUT_DIR)/%_test.txt: $(OUTPUT_DIR)/%_shuffled.fasttext
	tail -n 10000 $< > $@

$(OUTPUT_DIR)/%_normalized.txt: $(OUTPUT_DIR)/%.txt
	cat $< | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > $@

$(OUTPUT_DIR)/%.bin: $(OUTPUT_DIR)/%_training_normalized.txt
	fasttext supervised -input $< -output $(basename $@) -lr 1 -epoch 25 -wordNgrams 2


%.test: $(OUTPUT_DIR)/%.bin $(OUTPUT_DIR)/%_test_normalized.txt
	fasttext test $^ 1
	fasttext test $^ 5
	fasttext test $^ 10

%.clean:
	$(eval v := $(basename $@))
	rm -f $(OUTPUT_DIR)/${v}.bin
	rm -f $(OUTPUT_DIR)/${v}.vec
	rm -f $(OUTPUT_DIR)/${v}*.txt
	rm -f $(OUTPUT_DIR)/${v}*.fasttext

.PHONY: %.test %.clean
