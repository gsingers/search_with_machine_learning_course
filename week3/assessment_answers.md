## For classifying product names to categories:
### What precision (P@1) were you able to achieve?
0.833, with text preprocessing, min product count=200, category depth=3

### What fastText parameters did you use?
 -`epoch` 25 -`ngram` 2

### How did you transform the product names?
Stripped punctuation, Lowercased, Snowball Stemmng

### How did you prune infrequent category labels, and how did that affect your precision?
Implemented `min_product` parameter to enforce a minimum number of products per category for the thresholds 50, 100, 200

Results over different thresholds, with transformed product names:

| min_product | n_words | n_labels | P@1   | R@1   |
|-------------|---------|----------|-------|-------|
| 50          | 18347   | 512      | 0.667 | 0.667 |
| 100         | 15447   | 262      | 0.738 | 0.738 |
| 200         | 11773   | 113      | 0.829 | 0.829 |]


Increasing `min_product` increased our overall precision, but reduced the coverage of more infrequent category labels. Ther classifier achieves higher precision by discarding labels for which it would have lower confidence, so there is a conscious tradeoff to be made here

### How did you prune the category tree, and how did that affect your precision?

Results over different category depths, with transformed product names, and min_product=50:

| cat_depth | n_words | n_labels | P@1   | R@1   |
|-----------|---------|----------|-------|-------|
| 1         | 18347   | 512      | 0.667 | 0.667 |
| 2         | 20866   | 270      | 0.753 | 0.753 |
| 3         | 21116   | 93       | 0.799 | 0.799 |

Increasing the category depth increased the precision. This is because reducing the granularity of the categories to ancestor categories (i) reduced the number of unique categories, and (ii) increased the number of examples for each category to be learned

## For deriving synonyms from content:
### What 20 tokens did you use for evaluation?
Product types
- Headphones
- Phones
- Laptop
- Keyboard
- Camera

Brands
- Sony
- Apple
- Samsung
- Dell
- Panasonic

Models
- iphone
- thinkpad
- Xbox 360
- Ipad
- Inspiron

Attributes
- Black
- Silver
- Windows
- Mac
- Stainless Steel

### What fastText parameters did you use?
- `minCount` for 10, 20, 50

### How did you transform the product names?
Similar to Level 1: Stripped punctuation, Lowercased, Snowball Stemmng

### What threshold score did you use?
0.93 seemed to filter out most irrelevant nearest neighbours

### What synonyms did you obtain for those tokens?
| **query**       | **synonym**                                                                                                                                                                      |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| headphones      | headphon 0.987947, headset 0.933569, microphon 0.930466, iphon 0.916927, bluetooth 0.916876, ear 0.902065, cover 0.89258, handheld 0.891229, earbud 0.889798, skullcandi 0.88939 |
| phones          | phone 0.990643, motorola 0.972902, bluetooth 0.935118, cell 0.920713, nokia 0.917549, verizon 0.91178, blackberri 0.909021, mobil 0.908606, 4g 0.907648, headset 0.905597        |
| laptop          | inspiron 0.991764, i3 0.974365, vaio 0.973436, i5 0.971962, phenom 0.971684, notebook 0.970625, pentium 0.970142, eee 0.969638, lenovo 0.969034, dell 0.967414                   |
| keyboard        | sox 0.972937, musicskin 0.956999, scoreboard 0.95631, houston 0.953835, piano 0.952522, arizona 0.949018, patriot 0.941013, detroit 0.937053, riot 0.935204, diego 0.934042      |
| camera          | rebel 0.987884, easyshar 0.985918, canon 0.985639, powershot 0.984562, 0mp 0.984374, 2mp 0.983258, shot 0.981682, telephoto 0.981334, eo 0.981037, 1mp 0.980771                  |
| sony            | onyx 0.979699, deep 0.962531, factori 0.957017, ibm 0.951854, matt 0.946209, datel 0.945513, ceram 0.945272, ideapad 0.944013, delonghi 0.943984, messeng 0.940068               |
| apple           | speck 0.957051, sound 0.95444, miami 0.950016, russound 0.940206, outfit 0.940029, numark 0.939576, cincinnati 0.936033, arizona 0.934033, skullcandi 0.932286, stereo 0.930977  |
| samsung         | samsung 0.986607, lg 0.886898, sharp 0.882205, 32 0.855607, 120hz 0.833572, 720p 0.83153, 60hz 0.830947, aquo 0.828086, panason 0.823668, 1080p 0.823446                         |
| dell            | xentri 0.943158, cell 0.918245, htc 0.905712, evo 0.901603, no 0.897648, invisibleshield 0.896585, commut 0.895587, dell 0.891676, droid 0.886225, 4g 0.884393                   |
| panasonic       | panason 0.942421, b 0.836638, replac 0.834556, swiss 0.834111, camcord 0.828423, handycam 0.82678, cassett 0.82622, video 0.819915, record 0.819076, samsonit 0.813174           |
| iphone          | phone 0.946795, motorola 0.943585, iphon 0.941047, verizon 0.933045, bluetooth 0.924805, unlock 0.916583, blackberri 0.908568, 4g 0.904746, nokia 0.902537, shell 0.901644       |
| thinkpad        | ibm 0.973248, lenovo 0.965258, ideapad 0.954518, factori 0.95432, laptop 0.949409, vaio 0.942251, inspiron 0.941811, dell 0.938687, e 0.935412, eee 0.935337                     |
| xbox 360        | adventur 0.983541, nintendo 0.976829, advanc 0.97599, psp 0.97099, world 0.967499, gamecub 0.966938, ps3 0.965208, of 0.962659, wii 0.960982, tournament 0.956226                |
| ipad            | folio 0.989514, 3rd 0.963269, 4th 0.958918, tribeca 0.958223, 4s 0.954354, 3g 0.953308, generat 0.952774, nano 0.950117, otterbox 0.950056, charger 0.948895                     |
| inspiron        | laptop 0.991764, i3 0.984825, i5 0.984793, vaio 0.984777, phenom 0.984032, pentium 0.983787, intel 0.979056, pavilion 0.97754, processor 0.975267, aspir 0.975103                |
| black           | cleaner 0.877261, slider 0.874202, open 0.843965, white 0.843472, cellar 0.84054, orang 0.839546, gel 0.837472, glove 0.835101, cellular 0.829889, pure 0.824599                 |
| silver          | cyber 0.950368, handycam 0.946944, dcr 0.910118, camcord 0.906342, dsc 0.902267, lumix 0.901322, tripod 0.898695, blue 0.894917, red 0.893617, mini 0.891664                     |
| windows         | window 0.999168, edit 0.959025, of 0.955926, adventur 0.948302, wii 0.945745, world 0.94547, advanc 0.945223, gamecub 0.942082, 360 0.941311, nintendo 0.937693                  |
| steel           | bisqu 0.974568, stainless 0.973962, oven 0.972026, hood 0.97095, gas 0.967612, biscuit 0.966582, microwav 0.966115, maytag 0.965482, architect 0.960114, galleri 0.958254        |
| stainless steel | stainless 0.973962, oven 0.972026, hood 0.97095, gas 0.967612, biscuit 0.966582, microwav 0.966115, maytag 0.965482, architect 0.960114, galleri 0.958254                        |