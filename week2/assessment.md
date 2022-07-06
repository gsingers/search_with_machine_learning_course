# Week 2 Project Assessment
## For classifying product names to categories:
**What precision (P@1) were you able to achieve?**

I was able to achieve P@1 of 0.975, but I actually think the model is overfit.

**What fastText parameters did you use?**

Used  learning rate of 0.8, 25 epochs, and using bigrams.

**How did you transform the product names?**

I followed the basic steps outlined in the directions at this point which were: 
- remove non-alphanumeric characters, except for underscore ("_")
- convert all letters to lowercase
- trim excess space

```
def transform_name(product_name):
    # IMPLEMENT
    # remove nonalphanumeric characters except for spaces and underscores
    product_name = "".join([x for x in product_name if ((x.isalnum()) or (x == "_") or (x == " "))])
    # lowercase
    product_name = product_name.lower()
    # trim excess space
    product_name = re.sub(' +', " ", product_name)
    return product_name
```

**How did you prune infrequent category labels, and how did that affect your precision?**

I pulled the data into a pandas dataframe, performed a group by, and removed those labels with fewer than 500 examples. This improved P@1 by about 0.3, so a huge jump.

**How did you prune the category tree, and how did that affect your precision?**

Did not get to this optional piece.

## For deriving synonyms from content:

**What were the results for your best model in the tokens used for evaluation?**

**What fastText parameters did you use?**
epoch=25, minCount=20,

**How did you transform the product names?**

I applied `transform_name` as I defined it in `createContentTrainingData.py`

## For integrating synonyms with search:

**How did you transform the product names (if different than previously)?**

Same as above.

**What threshold score did you use?**

0.8. A large portion of the top words didn't actually have synonyms that exceeded this threshold, which was surprising to me.

**Were you able to find the additional results by matching synonyms?**

Yes and no. Since it seemed like an easy example (because the number of matches without synonyms was 8), I manually added `espresso,nespresso` to the synonyms file as this did match did not exceed the threshold in my original model. When running the query through `python utilities/query.py --synonyms`, I was able to see that more results were in fact returned. 

## For classifying reviews:

I did not do this optional part as of yet.

**What precision (P@1) were you able to achieve?**

**What fastText parameters did you use?**

**How did you transform the review content?**

**What else did you try and learn?**