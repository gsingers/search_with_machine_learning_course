Week4 Project
===
The following are the notes on the sub-tasks of W4 project.

Level 1: Query Classification
===

Before category rollup we had this many unique categories: 1 652 783

After rollup with min_queries = 100: 1 132 512

After rollup with min_queries=1000: 433 259



train:
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/labeled_query_data.txt.shuf.train -output /workspace/datasets/fasttext/labeled_query_data_1000 -loss hs -epoch 25

test:
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/labeled_query_data_1000.bin /workspace/datasets/labeled_query_data.txt.shuf.test



| min_queries | Stemming: Y/N | train   | test (10%) | P@1   | R@1   | P@3   | R@3   | P@5   | R@5   |
|-------------|---------------|---------|------------|-------|-------|-------|-------|-------|-------|
| 100         | **N**         | 1123975 | 124886     | **0.535** | **0.535** | 0.246 | 0.737 | 0.162 | 0.811 |
| 100         | Y             | 1150994 | 127888     | 0.532 | 0.532 | 0.244 | 0.733 | 0.162 | 0.809 |
| 1000        | **N**         | 446518  | 49613      | **0.633** | **0.633** | 0.264 | 0.791 | 0.17  | 0.85  |
| 1000        | Y             | 560886  | 62320      | 0.579 | 0.579 | 0.249 | 0.748 | 0.163 | 0.815 |


Level 2: Integrating Query Classification with Search
===
Queries that predicted with confidence >= 0.5 were let to filter by category. The model with min_queries=1000 was used in this experiment.

Worked quite well:

    macbook (pcmcat247400050001) -- brings good results with relevancy and category filtering
    tv antenna (abcat0107004) -- brings mounts on top when sorted by popularity and antennas when sorted by relevance
    microsoft office (abcat0508009) - brings mostly MS Office in top5
    lcd tv (abcat0101001) -- brings different TV makes, like Toshiba and LG


Not working so well:

    tablet (pcmcat209000050008) -- brings better results when sorted by popularity
    apple laptop (pcmcat247400050000) -- brings laptops of HP, Lenovo, Alienware -- no Apple at all on several scrolls
