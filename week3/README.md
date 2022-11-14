For query classification:

How many unique categories did you see in your rolled up training data when you set the minimum number of queries per category to 1000? To 10000?
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ cut -d' ' -f1 min_queries_100.csv | sort | uniq | wc
    878     878   21801
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ cut -d' ' -f1 min_queries_1000.csv | sort | uniq | wc
    387     387    9422

What were the best values you achieved for R@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category, as well as trying different fastText parameters or query normalization. Report at least 2 of your runs.

RUN 1 ( Min Queries: 10000):
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext supervised -input training_queries.txt -output query_classification -lr 0.8 -epoch 5 -wordNgrams 2
Read 0M words
Number of words:  11425
Number of labels: 387
Progress: 100.0% words/sec/thread:     771 lr:  0.000000 avg.loss:  3.932982 ETA:   0h 0m 0s

(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test query_classification.bin test_queries.txt 1
N       10000
P@1     0.542
R@1     0.542
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test query_classification.bin test_queries.txt 3
N       10000
P@3     0.244
R@3     0.732
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test query_classification.bin test_queries.txt 5
N       10000
P@5     0.159
R@5     0.795

===========================
Run 2( Min Queries: 1000)
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext supervised -input training_queries_100.txt -output query_classification_100 -lr 0.6 -epoch 5 -wordNgrams 2
Read 0M words
Number of words:  7667
Number of labels: 875
Progress: 100.0% words/sec/thread:     281 lr:  0.000000 avg.loss:  3.581045 ETA:   0h 0m 0s
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test query_classification_100.bin test_queries_100.txt 1
N       9998
P@1     0.524
R@1     0.524
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test query_classification_100.bin test_queries_100.txt 3
N       9998
P@3     0.235
R@3     0.704
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test query_classification_100.bin test_queries_100.txt 5
N       9998
P@5     0.153
R@5     0.766
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $

For integrating query classification with search:

Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure to include the classifier output for those queries.
For threshold 0.5 query classification wasn't giving category output for iphone category buy with threshold 0.2 I could see more relevant examples.
Cleaned Query :  iphon
Query : iphone, Query Classification : ['pcmcat209400050001']
['Apple® - iPhone 4 with 8GB Memory - White (AT&T)']
['Apple® - iPhone 4 with 8GB Memory - White (Verizon Wireless)']
['Apple® - iPhone 4 with 8GB Memory - Black (AT&T)']
['Apple® - iPhone 4 with 8GB Memory - White (Sprint)']
['Apple® - iPhone 4 with 8GB Memory - Black (Verizon Wireless)']
['Apple® - iPhone® 4S with 16GB Memory Mobile Phone - White (AT&T)']
['Apple® - iPhone® 4S with 16GB Memory Mobile Phone - Black (AT&T)']
['Apple® - iPhone® 4S with 16GB Memory Mobile Phone - White (Verizon Wireless)']
['Apple® - iPhone® 4 with 8GB Memory - Black (Sprint)']
['Apple® - iPhone® 4S with 16GB Memory Mobile Phone - Black (Verizon Wireless)']

---
With threshold 0.5
Cleaned Query :  iphon
Query : iphone, Query Classification : []
['ZAGG - InvisibleSHIELD HD for Apple® iPhone® 4 and 4S']
['LifeProof - Case for Apple® iPhone® 4 and 4S - Black']
['ZAGG - InvisibleSHIELD for Apple® iPhone® 4 - Clear']
['LifeProof - Case for Apple® iPhone® 4 and 4S - White']
['Rocketfish™ Mobile - Mini Stereo Cable for Apple® iPhone']
['Apple® - iPhone 4 with 8GB Memory - White (AT&T)']
['Rocketfish™ - Premium Vehicle Charger for Apple® iPad™, iPhone® and iPod®']
['ZAGG - Smudge Free Shield for Apple® iPhone® 4 and 4S']
['LifeProof - Case for Apple® iPhone® 4 and 4S - Pink']
['LifeProof - Case for Apple® iPhone® 4 and 4S - Purple']

Enter your query (type 'Exit' to exit or hit ctrl-c):
tv
Cleaned Query :  tv
Query : tv, Query Classification : ['abcat0101001']
['Magnavox - 15" HD-Ready LCD TV w/HD Component Video Inputs']
['Toshiba - 32" Class - LCD - 720p - 60Hz - HDTV']
['Samsung - 22" Class - LED - 1080p - 60Hz - HDTV']
['Insignia™ - 32" Class / LCD / 720p / 60Hz / HDTV']
['Insignia™ - 40" Class - LCD - 1080p - 60Hz - HDTV']
['Samsung - 32" Class - LED - 720p - 60Hz - HDTV']
['Westinghouse - 32" Class / LED / 720p / 60Hz / HDTV']
['Dynex™ - 32" Class / LCD / 720p / 60Hz / HDTV']
['Samsung - 32" Class - LCD -720p - 60Hz - HDTV']
['Insignia™ - 39" Class - LCD - 1080p - 60Hz - HDTV']
---------------------------------------------------
Cleaned Query :  keurig
Query : keurig, Query Classification : ['abcat0912009']
['Keurig - Elite Brewer - Black']
['Keurig - Mini Brewer - Platinum']
['Keurig - B70 Brewer - Platinum']
['Keurig - Refurbished Elite Brewer - Black']
['Keurig - Refurbished Mini Brewer - Black']
['Keurig - 1-Cup Mini Brewer - Red']
['Keurig - 1-Cup Mini Brewer - Black']
['Keurig - 1-Cup Mini Brewer - Black']
['Keurig - 1-Cup Mini Brewer - Red']
['Keurig - 1-Cup Mini Brewer - White']
------------------------------------------
juice maker
Cleaned Query :  juic maker
Query : juice maker, Query Classification : ['abcat0912000']
['Slushy Magic - Slushy Maker - Clear/Blue']
['Breville - Juice Fountain Compact Electric Juicer - Silver']
['DeLonghi - Juice Extractor']
['Oster - 400W Juice Extractor']
['Bella Cucina - Juice Extractor - White']
['Waring Pro - Refurbished Juice Extractor']
['Cuisinart - Juice Extractor - Stainless-Steel']
['Hamilton Beach - HealthSmart Juice Extractor - White']
['Hamilton - HealthSmart 67801 Juice Extractor - Black']
['Cuisinart - Refurbished Juice Extractor - Stainless-Steel']
-----------------------------------

Cleaned Query :  trimmer
Query : trimmer, Query Classification : ['abcat0915005']
["Norelco - Rechargeable Cordless Men's Razor"]
['Remington - Mini Trimmer']
['Philips Norelco - Stubble Trimmer']
['Wahl - Beard Trimmer - Gray']
['Philips Norelco - Cordless Nose and Ear Trimmer - Black']
['Remington - Beard and Mustache Trimmer']
['Wahl - Lithium Pen Trimmer - Blue']
['Remington - Precision Nose & Ear Trimmer']
['Conair - i-Stubble Hair Trimmer']
['Remington - Wet/Dry Goatee Trimmer']

Give 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some other reason. Again, include the classifier output for those queries.


Enter your query (type 'Exit' to exit or hit ctrl-c):
samsung phone
Cleaned Query :  samsung phone
Query : samsung phone, Query Classification : ['pcmcat158400050071']
['PayLo by Virgin Mobile - Kyocera S2100 No-Contract Mobile Phone - Cauldron Gray']
['AT&T GoPhone - Samsung A197 No-Contract Mobile Phone - Blue']
['T-Mobile - Samsung T239 Mobile Phone - Red']
['Jitterbug - Samsung No-Contract Mobile Phone - Red']
['Samsung Chrono No-Contract Phone & $25 Cricket Airtime Card Package']
['Claro - Samsung S5230 No-Contract Mobile Phone - Black']
['NET10 - Samsung 404G No-Contract Mobile Phone - Black']
['Virgin Mobile - Samsung Mantra No-Contract Cell Phone - Black/Silver']
['T-Mobile Prepaid - Samsung T249 No-Contract Mobile Phone - Blue/Gray']
['Cricket - Samsung MyShot II No-Contract Mobile Phone - Wine Red']


----------------------------
shaving cream
Cleaned Query :  shave cream
Query : shaving cream, Query Classification : ['abcat0912000']
['Hamilton - 68321 Ice Cream Maker']
['KitchenAid - Ice Cream Scoop - Black']
['Deni - Automatic Ice Cream Maker - Platinum']
['Deni - 2-Quart Ice Cream Maker']
['Discovery Kids - Toy Ice Cream Maker']
['Hamilton Beach - Rock Salt for Ice Cream Makers']
['Aroma - 4-Quart Ice Cream Maker - Pine']
['OXO - GOOD GRIPS Nonstick Ice Cream Scoop']
['Cuisinart - Frozen Yogurt/Ice Cream Maker - White']
['KitchenAid - Cook for the Cure Ice Cream Scoop - Pink']
-------------------------------

baby food
Cleaned Query :  babi food
Query : baby food, Query Classification : ['abcat0912000']
['Kalorik - Baby Food Maker - Yellow']
["Baby Chef - It's Just Right Digital Temperature Probe - White"]
['KitchenAid - Fruit and Vegetable Strainer Attachments for Most KitchenAid Stand Mixers']
['Hamilton Beach - Bébé 3-Cup Food Chopper - White']
['Panasonic - 4.1-Quart Electric Thermal Pot - White/Silver']
['Panasonic - 3.2-Quart Electric Thermal Pot - White/Silver']
['Panasonic - 2.3-Quart Electric Thermal Pot - White']
['Deni - Food Slicer']
['Siemens - Food Processor']
['Kalorik - Food Processor - Black']
