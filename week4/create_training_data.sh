# Create labeled data with min queries
declare -a MIN_QUERIES=(100 300 500 700 1000)

for i in "${MIN_QUERIES[@]}"
do
    FILE=/workspace/datasets/labeled_query_data_$i.txt     
    if test -f "$FILE"; then
        rm -f "$FILE"
    fi
    python /workspace/search_with_machine_learning_course/week4/create_labeled_queries.py --min_queries ${i}
done