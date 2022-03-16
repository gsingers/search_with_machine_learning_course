Week4 Project
===
The following are the notes on the sub-tasks of W4 project.

Level 1: Query Classification
===

Before category rollup we had this many unique categories: 1 652 783

After rollup with min_queries = 100: 1 132 512

After rollup with min_queries=1000: 433 259



| min_queries | Stemming: Y/N | train   | test (10%) | P@1   | R@1   | P@3   | R@3   | P@5   | R@5   |
|-------------|---------------|---------|------------|-------|-------|-------|-------|-------|-------|
| 100         | N             | -       | 124886     | 0.535 | 0.535 | 0.246 | 0.737 | 0.162 | 0.811 |
| 100         | Y             | 1150994 | 127888     | 0.532 | 0.532 | 0.244 | 0.733 | 0.162 | 0.809 |
| 1000        | N             | 446518  | 49613      | 0.633 | 0.633 | 0.264 | 0.791 | 0.17  | 0.85  |
| 1000        | Y             | 560886  | 62320      | 0.579 | 0.579 | 0.249 | 0.748 | 0.163 | 0.815 |

