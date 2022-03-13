See [Week 3 Notebook](week4.ipynb) for experiment run details.

## Query Classification:

How many unique categories did you see in your rolled up training data
when you set the minimum number of queries per category to 100? To 1000?

In my initial implementation, one iteration step would rollup all categories
with less than min queries. With that the numbers were:

- 100: 880 categories
- 1000: 388 categories

Later I switched to a different logic where in one iteration it would only
transform leaf categories (leaves of remaining categories). Numbers slightly
changed as below:

- 100: 888
- 1000: 404

---

What values did you achieve for P@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category as well as trying different fastText parameters or query normalization. Report at least 3 of your runs.

With min categories = 100

| Parameters                   | P@1 | R@3 | R@5 |
| ---------------------------- | --- | --- | --- |
| epochs=5 lr=.1 ngrams=1      | .47 | .62 | .68 |
| epochs=5 **lr=.5** ngrams=1  | .52 | .70 | .76 |
| **epochs=25** lr=.1 ngrams=1 | .52 | .70 | .76 |
| **epochs=25 lr=.5** ngrams=1 | .51 | .70 | .75 |
| epochs=5 **lr=.5 ngrams=2**  | .51 | .70 | .76 |

With min categories = 1000

| Parameters                   | P@1 | R@3 | R@5 |
| ---------------------------- | --- | --- | --- |
| epochs=5 lr=.1 ngrams=1      | .48 | .64 | .71 |
| epochs=5 **lr=.5** ngrams=1  | .53 | .71 | .77 |
| **epochs=25** lr=.1 ngrams=1 | .53 | .71 | .77 |
| **epochs=25 lr=.5** ngrams=1 | .52 | .71 | .77 |
| epochs=5 **lr=.5 ngrams=2**  | .53 | .71 | .78 |
 
---

## Integrating query classification with search:

### Where it works well

It works really well for categories where products have lots
of accessories - it does a good job of surfacing the actual product
whereas a accessory specific query works well for accessory too.

For eg:
#### fuji camera
```
abcat0401004 0.55 Fun & Basic Cameras
```

Top results are all digital cameras. Without classification, top results were for
digital camera starter kits.

#### thinkpad
```
pcmcat247400050000 0.32 PC Laptops
abcat0504010 0.12 USB Flash Drives
pcmcat209000050008 0.09 Tablets
```

Without classification, it shows batteries, cables and other accessories. Works great
with classification with all top results being thinkpad laptops.

---

As a variation of above, a query of the form __BRAND + CATEGORY__ results
in good matches for products of that brand in that category. For eg.

#### sony computer
Garbage results without classification. With classification, top results are all for __sony vaio__

---

Other examples

#### usb stick
```
abcat0504010 0.35 USB Flash Drives
abcat0507011 0.1 USB & FireWire Cards
pcmcat147700050013 0.096 Xbox 360 Memory & Hard Drives
```

Without classification, top results were card readers, adapters etc. Shows usb drives with classification

#### ps3
```
abcat0703001 0.51 PS3 Consoles
```
No ps3 in top pages without classification. Top result with classification.


#### blu ray drive
```
pcmcat189600050010 0.31 Internal DVD Drives
abcat0504008 0.15 Blu-ray Drives
pcmcat189600050009 0.12 External DVD Drives
```

Without classification, top results were couple of laptops, and then a lot of blu ray music discs. Worked great with classification.

---

### Where it doesn't work well

#### apple tablet
Without classification, some of the top results were:
- Toshiba - Back Cover for Toshiba Thrive Tablets - Green Apple
- Logitech - Tablet Keyboard for Apple® iPad®, iPad 2 and iPad (3rd Generation)
- Timbuk2 - Catapult Sling for Apple® iPad® and up to 10" Tablets - Gray/Blue

With classification, current model returned the following categories:
```
transformed = appl tablet
pcmcat209000050007 0.34 iPad
pcmcat209000050008 0.16 Tablets
```

It got rid of the accessories, but second category `Tablets` really hurt results,
as most hits are other tablets which have "tablet" string in their name.

I do wonder if it was possible to figure out that in query "apple tablet", the first
word is a named entity and the second word is the category, so somehow give more 
boost to apple in the name matching.

An earlier model with slight different logic for rolling up queries worked great for this
query though - so even minor changes can affect prominent queries.

#### nas drive
Didn't turn up any NAS drive. There is a category `abcat0504004` (Network and tablet hard drives) and there are 8 queries for nas drive in `train.csv` which all map to this category. So, probably it would have worked fine if the training data size was much larger.

#### music player
This example show where query classification with filtering really hurts. 
The classified category was:
```
cat02015 0.11 Movies & TV Shows
```

In this case, top results were really good *without* query classification. Whereas with
classification they were all garbage.

Further analysis showed different results when playing with different parameters.
Actual predictions from fasttext were:
```
                       name     score            category
0         Movies & TV Shows  0.112161            cat02015
1               MP3 Players  0.085276        abcat0201010
2         iTunes Gift Cards  0.049240        abcat0201007
3                Turntables  0.048174        abcat0202007
4  All Home Theater Systems  0.036608  pcmcat167300050040
```

I was running with a minimum threshold of .1 which gets rid of "MP3 Players". If I
change the minimum threshold to .05 or remove it, results look much better. So maybe
in case of filtering, it is more important to have more categories to improve recall
if top category match is not strong - though it can also hurt in some cases like
"apple tablet" above.
