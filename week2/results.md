### SWML Week 2 project questions
1.- For classifying product names to categories:
    1. 1.-What precision (P@1) were you able to achieve?
		0.85@P1 with pruned categories, training a model with pruned data with only ~28K product names and labels, after getting to the last step of the exercise. The increase was notable step 2 to 3 , and from 3 to 6, affecting the most the results the learning rate, the epochs, and the trimmed down dataset Full evolution goes like this:                1.- ~0.16@P1, w raw data, 1 epoch, and default learning rate, to 
	        2.- ~0.61@P1, w raw data, 25 epochs, and learning rate set to 1.0, to
		3.- 0.616@P1 with normalised data (keeping most alnum characters ,lowercasing), w 25 epochs and lr to 1.0,to
                 4.- 0.74@P1 with pruned data for products whose categories are present in at least 500 products, default epochs and learning rate, to
                 5.- 0.74@P1 with above configuration, but now with 25 epochs and learning rate set to 1,0, to
		6.- 0.80@P1 with above configuration, but with training model with wordngrams set to 2
		7.- 0.821@P1 with above configuration, but with training model with wordngrams set to 3, same with wordngrams set to 4, to
		8.- 0.85@P1 by normalising the pruned data like in step 3, with wordngrams set to 3, epochs to 25 and learning rate to 1.0

1.2.-What fastText parameters did you use? I used the ones in the exercise explanation :
 - epochs -> from 1 (default)  incrementally to 25. I learned that epoch increment made the most improvement on the first stage
-learning rate  -> from the default one , to 1. It did not help as much but it helped increasing the precision @ 1 by a small percentage
1.3.-How did you transform the product names?- I applied the command in the week 2 section 1 exercise, that removed punctuation (minus underscore characters) , lowercased letters, and trimmed spaces to just one
1.4.-How did you prune infrequent category labels, and how did that affect your precision?
- I used pandas for that, I created a DataFrame that grouped the name<->category pairs, and if a —min_products was passed, I filtered down the df to the ones that had equal or greater product counts. For a min_products of 500, it boiled the dataset down to 28921 product entries with their corresponding categories. 

5.- How did you prune the category tree, and how did that affect your precision?
(Did not do the optional)—————————————————————————————————————————————————————————————————————
2.-  For deriving synonyms from content:
2.1.-What were the results for your best model in the tokens used for evaluation?
product_synonyms_mc100_e25
---------------------------
headphones
earbud 0.892993
ear 0.892619
bud 0.682221

laptop
laptops 0.774181
notebook 0.757335
notebooks 0.6235

freezer
freezers 0.841545
refrigerator 0.760481
refrigerators 0.74623

nintendo
ds 0.943314
wii 0.880049
3ds 0.739917

whirlpool
maytag 0.840322
frigidaire 0.785068
biscuit 0.747542

kodak
easyshare 0.818913
canon 0.613138
photosmart 0.539153

ps2
playstation 0.790947
xbox 0.702776
psp 0.672368

razr
razer 0.844175
gaming 0.549824
geforce 0.496215
oakland 0.465064

stratocaster
roaster 0.66059
toaster 0.660496
pots 0.621303

holiday
day 0.624485
miami 0.599781
birthday 0.591433

plasma
600hz 0.69296
tvs 0.646175
televisions 0.637813
flat 0.60527


leather
recliner 0.651175
executive 0.568764
berkline 0.548568

product_synonyms
---------------------------
headphones
headphone 0.9331
earbud 0.87707
ear 0.871433

laptop
laptops 0.840583
notebook 0.718399
laps 0.700666

freezer
freezers 0.924926
freezerless 0.910565
frost 0.82156

nintendo
nintendogs 0.961595
ds 0.905364
wii 0.876882

whirlpool
maytag 0.851012
whirl 0.844564
biscuit 0.840229

kodak
easyshare 0.873411
c813 0.746543
m763 0.743608

ps2
playstation 0.813392
psn 0.795362
2k5 0.755396

razr
krzr 0.883039
a855 0.875047
r225 0.871493

stratocaster     
telecaster 0.893341
starcaster 0.878198
strat 0.842983

holiday
holidays 0.959102
thanks 0.823975
congrats 0.813394

plasma
600hz 0.874522
hdtvs 0.794404
xbr 0.790108

leather
leatherskin 0.890925
recliner 0.711402
berkline 0.664858
2.2.-What fastText parameters did you use?
      - I used number of epochs incrementally until 25, with some effect on “Other” keywords that did not retrieve synonyms (IE stratocaster on minimumCount 100 and maxwords 0)
       - minCount set to 100 helped on some words to provide synonyms related to stemming (ie freezer->freezers) but it shuffled a bit the ordering of results.
2.3.-How did you transform the product names?
      - I did the same transformation as the one required in the activity, which is to lowercase, trim spaces, remove punctuation,and keep alnum characters 
—————————————————————————————————————————————————————————————————————
For integrating synonyms with search:
1. How did you transform the product names (if different than previously)?
      - I did not change the transformation names from the one specified in the exercise
1. What threshold score did you use?The threshold score I did use was 0.75 for a trained set whose epoch quantity is 25 and its miscount is equal to 100.
2. Were you able to find the additional results by matching synonyms? 
	- Just found a few of them but numbers did not increase as much. Also I had timeout errors when calling to the query.py script 

