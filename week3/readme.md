## Setup environment
pyenv activate search_with_ml_week3
alias fasttext=~/fastText-0.9.2/fasttext
pip install nltk fasttext
// pip install ipython pandas lxml
// pip install elementpath

## First run
python week3/createContentTrainingData.py

cat /workspace/datasets/fasttext/output.fasttext | sort -R > /workspace/datasets/fasttext/output.fasttext.rand
head -n -10000 /workspace/datasets/fasttext/output.fasttext.rand > /workspace/datasets/fasttext/output.fasttext.train
tail -10000 /workspace/datasets/fasttext/output.fasttext.rand > /workspace/datasets/fasttext/output.fasttext.test

// train
fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs

// test
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       9983
P@1     0.643
R@1     0.643

N       9983
P@5     0.168
R@5     0.842

P@10    0.0883
R@10    0.883

fasttext predict prod_cat.bin -


fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       9983
P@1     0.739
R@1     0.739

N       9983
P@5     0.186
R@5     0.894

N       9983
P@10    0.104
R@10    0.918


---

## Implement transform_name

python week3/createContentTrainingData.py

head /workspace/datasets/fasttext/output.fasttext

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       9984
P@1     0.737
R@1     0.737

N       9984
P@5     0.185
R@5     0.887

N       9984
P@10    0.104
R@10    0.91



## min products


python week3/createContentTrainingData.py --min_products=50

> categories ignored = 1432
> categories written = 520

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.801
R@1     0.801

N       10000
P@5     0.195
R@5     0.939

N       10000
P@10    0.114
R@10    0.958


python week3/createContentTrainingData.py --min_products=200

> categories ignored = 1839
> categories written = 113

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.903
R@1     0.903

N       10000
P@5     0.214
R@5     0.987

N       10000
P@10    0.144
R@10    0.993

## sample rate

python week3/createContentTrainingData.py --min_products=50 --sample_rate=0.3

> categories ignored = 1558
> categories written = 142

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.826
R@1     0.826

N       10000
P@5     0.201
R@5     0.962

N       10000
P@10    0.122
R@10    0.977

## category depth

python week3/createContentTrainingData.py --min_products=200 --cat_depth=2

> categories ignored = 273
> categories written = 149

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.878
R@1     0.878

N       10000
P@5     0.212
R@5     0.974

N       10000
P@10    0.139
R@10    0.983


python week3/createContentTrainingData.py --min_products=100 --cat_depth=2

> categories ignored = 214
> categories written = 208

N       10000
P@1     0.861
R@1     0.861

N       10000
P@5     0.209
R@5     0.966

N       10000
P@10    0.133
R@10    0.977


python week3/createContentTrainingData.py --min_products=50 --cat_depth=2

> categories ignored = 152
> categories written = 270

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.844
R@1     0.844

N       10000
P@5     0.205
R@5     0.954

N       10000
P@10    0.128
R@10    0.974



python week3/createContentTrainingData.py --min_products=50 --cat_depth=4

> categories ignored = 34
> categories written = 92

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.872
R@1     0.872

N       10000
P@5     0.228
R@5     0.977

N       10000
P@10    0.159
R@10    0.985

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 0.1 -epoch 50 -wordNgrams 2

## max products - categories balanced

python week3/createContentTrainingData.py --min_products=50 --max_products=50 

> categories ignored = 1432
> categories written = 520


fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.709
R@1     0.709

N       10000
P@5     0.174
R@5     0.867

N       10000
P@10    0.0936
R@10    0.908


python week3/createContentTrainingData.py --min_products=50 --max_products=50 --sample_rate=0.3

> categories ignored = 1553
> categories written = 155

$ cat /workspace/datasets/fasttext/output.fasttext | wc -l
> 7595

No point in training.


python week3/createContentTrainingData.py --min_products=50 --max_products=50 --cat_depth=2

> categories ignored = 152
> categories written = 270

$ cat /workspace/datasets/fasttext/output.fasttext | wc -l
> 13230

No point in training.


python week3/createContentTrainingData.py --min_products=200 --max_products=200

> categories ignored = 1839
> categories written = 113

$ cat /workspace/datasets/fasttext/output.fasttext | wc -l
> 22487


fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.883
R@1     0.883

N       10000
P@5     0.198
R@5     0.978

N       10000
P@10    0.12
R@10    0.99


# Level 2 - synonyms


## First run
python week3/extractTitles.py
python week3/synonyms.py

```
brands 
 apple                           ~> iSimple         (99.97%)    Maple           (99.96%)        Watchband       (99.96%) 
 Sony                            ~> Cassette        (99.97%)    8GB*            (99.96%)        Basix           (99.95%) 
 Ubisoft                         ~> Santa           (99.96%)    Netgear         (99.96%)        Technology      (99.96%) 
 Whirlpool                       ~> Free            (99.97%)    White/Blue      (99.96%)        Over-the-Range  (99.96%) 
 Dell                            ~> Turion™         (99.96%)    Init™           (99.96%)        Inspire         (99.96%) 
product types 
 Tablet                          ~> Tablets         (100.00%)   Keystone        (99.98%)        Bluetooth-Enabled (99.98%) 
 Hard Drive                      ~> Drive           (99.96%)    32GB            (99.95%)        1TB             (99.94%) 
 Notebook                        ~> Notebooks       (99.99%)    Songbook        (99.99%)        Essentials      (99.98%) 
 Smartphone                      ~> Smartphones     (99.99%)    Saxophone       (99.98%)        Jawbone         (99.97%) 
 Gaming Keyboard                 ~> Houston         (99.99%)    Adventures      (99.98%)        Minnesota       (99.98%) 
models 
 VAIO                            ~> Asus            (99.96%)    15W             (99.95%)        4G              (99.94%) 
 Game Boy Advance                ~> Advanced        (99.97%)    Advance         (99.95%)        Time            (99.95%) 
 Nikkor                          ~> Calculator      (99.92%)    Order)          (99.89%)        Sigma           (99.86%) 
attribute 
 4GB                             ~> GB              (99.94%)    64GB            (99.92%)        6GB             (99.90%) 
 Black                           ~> black           (99.93%)    Black/Orange    (99.89%)        Blackjack       (99.87%) 
 Windows                         ~> Windows,        (99.99%)    Window          (99.99%)        Mac/Windows     (99.97%) 
 MP3 Playback                    ~> Radar           (99.97%)    Radica          (99.97%)        20-Pack         (99.97%) 
 24"                             ~> Tub             (99.95%)    Built-in        (99.89%)        Built           (99.87%)
 ```


 ## Normalize the product names

$ python week3/extractTitles.py

$ head /workspace/datasets/fasttext/titles.txt
> orphen scion of sorcery playstation 2 ps2
> delorme earthmate pn60w gps black
> numark refurbished mixdeck dj system blacksilv
> memorex slim jewel cases 30pack assort

$ python week3/synonyms.py

```
brands 
 appl                            ~> iphon           (99.88%)    ipad            (99.87%)        4thgeneration   (99.87%) 
 soni                            ~> songs           (99.99%)    lets            (99.99%)        sonax           (99.99%) 
 ubisoft                         ~> mice            (99.99%)    hitch           (99.99%)        fram            (99.98%) 
 whirlpool                       ~> free            (99.99%)    frigidaire      (99.99%)        freezer         (99.98%) 
 dell                            ~> hardshell       (99.99%)    desk            (99.98%)        allinone        (99.98%) 
product types 
 tablet                          ~> tablets         (100.00%)   tabletop        (99.99%)        outlet          (99.99%) 
 hard driv                       ~> drive           (99.97%)    1tb             (99.97%)        hard            (99.96%) 
 notebook                        ~> lifebook        (100.00%)   nook            (99.99%)        book            (99.99%) 
 smartphon                       ~> verizon         (99.98%)    snapon          (99.98%)        headset         (99.98%) 
 gaming keyboard                 ~> keyboards       (99.99%)    patriots        (99.99%)        indianapolis    (99.99%) 
models 
 vaio                            ~> laptops         (99.98%)    accessory       (99.98%)        pentium         (99.98%) 
 game boy adv                    ~> game            (99.99%)    gamecub         (99.99%)        gamecube        (99.98%) 
 nikkor                          ~> with            (99.95%)    210             (99.92%)        250             (99.92%) 
attribute 
 4gb                             ~> gb              (99.97%)    6gb             (99.96%)        8gb             (99.95%) 
 black                           ~> blackr          (99.98%)    orang           (99.97%)        rangers         (99.97%) 
 window                          ~> windows         (100.00%)   macwindow       (99.99%)        wind            (99.99%) 
 mp3 playback                    ~> playback        (99.99%)    lite            (99.99%)        moshi           (99.99%) 
 24                              ~> bisqueonbisqu   (99.94%)    dishwasher      (99.94%)        bisqu           (99.94%)
```


## Experiment with the minCount

$ python week3/synonyms.py --epoch=25

```
brands 
 appl                            ~> apple           (95.57%)    ipad            (87.10%)        4               (84.50%) 
 soni                            ~> sonic           (86.00%)    sonax           (74.91%)        songs           (71.65%) 
 ubisoft                         ~> soft            (71.75%)    microsoft       (71.73%)        2005            (71.27%) 
 whirlpool                       ~> maytag          (94.51%)    biscuit         (93.32%)        biscuitonbiscuit (93.08%) 
 dell                            ~> phenom          (82.37%)    64              (80.84%)        pentium         (80.83%) 
product types 
 tablet                          ~> tablets         (94.83%)    tabletop        (91.50%)        table           (87.91%) 
 hard driv                       ~> hard            (93.70%)    320gb           (89.89%)        750gb           (89.00%) 
 notebook                        ~> lifebook        (89.33%)    netbook         (89.27%)        ultrabook       (83.91%) 
 smartphon                       ~> phon            (87.46%)    snapon          (80.11%)        headset         (78.12%) 
 gaming keyboard                 ~> keyboard        (90.66%)    keyboards       (84.87%)        motherboard     (80.57%) 
models 
 vaio                            ~> e               (90.07%)    133             (87.57%)        duo             (85.08%) 
 game boy adv                    ~> game            (98.94%)    gamecub         (93.99%)        gamecube        (92.28%) 
 nikkor                          ~> refractor       (78.98%)    hydride         (78.86%)        gladiator       (74.18%) 
attribute 
 4gb                             ~> 8gb             (96.46%)    12gb            (95.38%)        3gb             (95.05%) 
 black                           ~> blackr          (92.15%)    blackjack       (90.21%)        blueblack       (89.10%) 
 window                          ~> macwindow       (96.10%)    windows         (95.53%)        08              (82.48%) 
 mp3 playback                    ~> playback        (98.54%)    5disc           (84.45%)        cd              (84.20%) 
 24                              ~> tub             (92.30%)    dishwasher      (90.03%)        bisqueonbisqu   (86.34%)
```

$ python week3/synonyms.py --epoch=25 --minCount=50

```
brands 
 appl                            ~> apple           (97.78%)    ipad            (79.30%)        ipod            (78.54%) 
 soni                            ~> sony            (81.82%)    panasonic       (78.35%)        kodak           (66.48%) 
 ubisoft                         ~> microsoft       (90.85%)    360             (66.64%)        xbox            (65.08%) 
 whirlpool                       ~> frigidaire      (94.43%)    maytag          (92.13%)        whiteonwhit     (90.50%) 
 dell                            ~> inspiron        (82.70%)    desktop         (78.61%)        pavilion        (75.01%) 
product types 
 tablet                          ~> portable        (86.37%)    cable           (71.90%)        expandable      (62.15%) 
 hard driv                       ~> hard            (96.58%)    500gb           (91.99%)        drive           (89.70%) 
 notebook                        ~> netbook         (87.31%)    laptop          (76.98%)        core            (72.87%) 
 smartphon                       ~> vacuum          (79.82%)    phon            (79.35%)        smart           (72.06%) 
 gaming keyboard                 ~> keyboard        (92.46%)    leonard         (60.36%)        collection      (58.96%) 
models 
 vaio                            ~> radio           (80.14%)    audio           (75.13%)        av              (62.76%) 
 game boy adv                    ~> game            (95.49%)    adv             (90.81%)        boy             (86.17%) 
 nikkor                          ~> nikon           (84.46%)    extra           (80.75%)        camera          (80.29%) 
attribute 
 4gb                             ~> memory          (89.89%)    8gb             (88.24%)        500gb           (82.98%) 
 black                           ~> whit            (68.73%)    r               (65.13%)        white           (64.97%) 
 window                          ~> macwindow       (95.12%)    edition         (69.66%)        xbox            (69.04%) 
 mp3 playback                    ~> mp3             (77.02%)    player          (71.49%)        2gb             (69.40%) 
 24                              ~> tub             (96.89%)    tall            (95.31%)        dishwasher      (94.00%) 
```


$ python week3/synonyms.py --epoch=25 --minCount=50 --model=skipgram

```
brands 
 appl                            ~> apple           (97.76%)    ipad            (75.30%)        ipod            (74.25%) 
 soni                            ~> sony            (86.39%)    panasonic       (85.77%)        jvc             (68.16%) 
 ubisoft                         ~> microsoft       (93.26%)    360             (66.23%)        edition         (62.20%) 
 whirlpool                       ~> maytag          (91.63%)    frigidaire      (91.36%)        whiteonwhit     (84.26%) 
 dell                            ~> inspiron        (88.57%)    asus            (80.41%)        pavilion        (77.85%) 
product types 
 tablet                          ~> portable        (90.16%)    gp              (69.51%)        cable           (66.94%) 
 hard driv                       ~> hard            (96.34%)    drive           (85.70%)        500gb           (84.89%) 
 notebook                        ~> netbook         (83.73%)    laptop          (73.04%)        intel           (68.50%) 
 smartphon                       ~> smart           (81.01%)    phon            (80.50%)        vacuum          (75.64%) 
 gaming keyboard                 ~> keyboard        (95.05%)    mouse           (67.37%)        leonard         (65.33%) 
 iphon                           ~> iphone          (89.43%)    shell           (79.01%)        ipad            (78.84%) 
models 
 vaio                            ~> radio           (78.88%)    audio           (76.76%)        vacuum          (75.28%) 
 game boy adv                    ~> game            (95.70%)    adv             (89.11%)        games           (85.69%) 
 nikkor                          ~> nikon           (87.57%)    eos             (78.93%)        slr             (78.30%) 
attribute 
 4gb                             ~> 8gb             (75.96%)    2gb             (74.70%)        memory          (70.16%) 
 black                           ~> blackonblack    (66.72%)    r               (63.74%)        silv            (61.62%) 
 window                          ~> macwindow       (94.32%)    edition         (71.29%)        xbox            (64.61%) 
 mp3 playback                    ~> mp3             (75.06%)    player          (67.47%)        play            (65.30%) 
 24                              ~> tall            (84.54%)    tub             (82.35%)        dishwasher      (81.05%)
```


## Full sample

python week3/extractTitles.py --sample_rate=1

python week3/synonyms.py --epoch=25 --minCount=50 --model=skipgram

```
brands 
 appl                            ~> apple           (84.95%)    iphone          (70.51%)        ipod            (70.39%) 
 soni                            ~> sonic           (83.59%)    toothbrush      (51.59%)        sonax           (50.86%) 
 ubisoft                         ~> soft            (64.71%)    microsoft       (63.01%)        mitsubishi      (58.60%) 
 whirlpool                       ~> maytag          (74.48%)    biscuitonbiscuit (71.35%)       frigidaire      (66.48%) 
 dell                            ~> inspiron        (88.33%)    xps             (74.03%)        acer            (69.08%) 
product types 
 tablet                          ~> tablets         (67.64%)    archos          (55.24%)        tab             (53.35%) 
 hard driv                       ~> hard            (78.97%)    drive           (76.43%)        drives          (69.95%) 
 notebook                        ~> laptop          (68.83%)    briefcase       (51.12%)        targus          (49.60%) 
 smartphon                       ~> phon            (71.47%)    smart           (69.71%)        240hz           (60.02%) 
 gaming keyboard                 ~> keyboard        (82.97%)    gaming          (70.27%)        keyboards       (62.95%) 
 iphon                           ~> iphone          (74.97%)    apple           (68.60%)        ipod            (58.97%) 
models 
 vaio                            ~> dell            (63.73%)    inspiron        (61.55%)        155             (60.87%) 
 game boy adv                    ~> game            (83.21%)    boy             (81.05%)        adv             (80.88%) 
 nikkor                          ~> 30110mm         (73.97%)    10mm            (72.62%)        j1              (71.56%) 
attribute 
 4gb                             ~> 8gb             (81.76%)    memory          (76.94%)        2gb             (75.41%) 
 black                           ~> silv            (67.97%)    whit            (67.96%)        blacksilv       (64.29%) 
 window                          ~> macwindow       (81.00%)    edition         (61.36%)        adv             (60.86%) 
 mp3 playback                    ~> playback        (99.03%)    facepl          (70.02%)        cd              (67.87%) 
 24                              ~> tub             (67.07%)    tall            (65.18%)        dishwasher      (60.81%)
```

python week3/synonyms.py --epoch=50 --minCount=50 --model=skipgram

```
brands 
 appl                            ~> apple           (83.29%)    ipod            (72.48%)        iphone          (71.38%) 
 soni                            ~> sonic           (83.10%)    songbook        (46.48%)        toothbrush      (46.40%) 
 ubisoft                         ~> mitsubishi      (61.41%)    microsoft       (60.03%)        soft            (59.97%) 
 whirlpool                       ~> maytag          (76.80%)    biscuitonbiscuit (69.45%)       frigidaire      (67.75%) 
 dell                            ~> inspiron        (86.20%)    acer            (70.20%)        xps             (67.49%) 
product types 
 tablet                          ~> tablets         (60.31%)    archos          (56.62%)        101             (52.20%) 
 hard driv                       ~> hard            (75.03%)    drives          (69.67%)        drive           (69.45%) 
 notebook                        ~> laptop          (67.45%)    briefcase       (50.39%)        targus          (47.97%) 
 smartphon                       ~> phon            (68.91%)    smart           (63.91%)        phones          (55.88%) 
 gaming keyboard                 ~> keyboard        (81.24%)    gaming          (71.50%)        steelseries     (59.27%) 
 iphon                           ~> iphone          (72.28%)    apple           (60.13%)        ipod            (55.28%) 
models 
 vaio                            ~> dell            (64.68%)    155             (58.03%)        inspiron        (55.28%) 
 game boy adv                    ~> boy             (81.88%)    game            (81.60%)        adv             (80.87%) 
 nikkor                          ~> 30110mm         (68.35%)    f28             (67.40%)        10mm            (66.77%) 
attribute 
 4gb                             ~> 8gb             (82.87%)    memory          (80.02%)        2gb             (75.28%) 
 black                           ~> whit            (70.05%)    silv            (67.27%)        blu             (66.44%) 
 window                          ~> macwindow       (83.12%)    d               (61.39%)        adv             (61.25%) 
 mp3 playback                    ~> playback        (99.01%)    changer         (67.82%)        facepl          (65.01%) 
 24                              ~> tall            (65.31%)    tub             (64.20%)        dishwasher      (58.11%)
```


python week3/synonyms.py --epoch=50 --minCount=50 --treshold=0.75
```
brands 
 apple                           ~> ipod            (79.66%)    iphone          (76.11%) 
 sony                            ~> 
 ubisoft                         ~> 
 whirlpool                       ~> 
 dell                            ~> 
product types 
 tablet                          ~> 
 hard drive                      ~> drive           (88.70%)    hard            (81.60%) 
 notebook                        ~> notebooks       (76.84%) 
 smartphone                      ~> smartphones     (91.16%) 
 gaming keyboard                 ~> keyboard        (79.16%) 
 iphone                          ~> apple           (76.11%) 
models 
 vaio                            ~> 
 game boy advance                ~> advance         (88.45%)    boy             (81.52%) 
 nikkor                          ~> 
attribute 
 4gb                             ~> 8gb             (87.39%)    2gb             (84.08%)        3gb             (81.13%) 
 black                           ~> blackwhite      (80.20%)    blackgray       (78.58%)        blacksilver     (78.45%) 
 windows                         ~> macwindows      (86.89%) 
 mp3 playback                    ~> playback        (94.99%) 
 24                              ~> 
```

# Self-assesment

To assess your project work, you should be able to answer the following questions:

- For classifying product names to categories:
    - What precision (P@1) were you able to achieve?
      ```
      0.883
      ```

    - What fastText parameters did you use?
      ```
      -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
      ```

    - How did you transform the product names?
      ```
      Use english stemer
      Remove punctuations
      ```
    
    - How did you prune infrequent category labels, and how did that affect your precision?
      ```
      min_products = 200 show biggest difference for P@1 & R@1
      > categories ignored = 1839
      > categories written = 113
      > P@1     0.903
      > R@1     0.903
      > P@10    0.144
      > R@10    0.993
      
      Introucing max_products=200 to create balance categories show
      min_products = 200 show decrese on P@1 & R@1
      Which makes me belive high metrics previouse were subject to class inbalance

      > categories ignored = 1839
      > categories written = 113
      > P@1     0.883
      > R@1     0.883
      > P@10    0.12
      > R@10    0.99
      ```

    - How did you prune the category tree, and how did that affect your precision?
      ```
      Didn't change a lot. 
      
      Of cource for root category it was 
      P@1     1
      R@1     1

      but of cource it was only one category to predict.
      ```
     

- For deriving synonyms from content:
    - What 20 tokens did you use for evaluation?
      ```
      Are few lines above
      ```

    - What fastText parameters did you use?
      ```
      --epoch=50 --minCount=50 --model=skipgram
      --epoch=50 --minCount=50 --model=cbow
      ```

    - How did you transform the product names?
    ```
    Steam
    Remove punctuation
    ```

    - What threshold score did you use? 
    ```
    None, listed k=3 
    ```

    - What synonyms did you obtain for those tokens?
    ```
    Are few lines above are examples
    ```

For integrating synonyms with search: (Skipped)
    - How did you transform the product names (if different than previously)?
    - What threshold score did you use?
    - Were you able to find the additional results by matching synonyms?

For classifying reviews: (Skipped)
    - What precision (P@1) were you able to achieve?
    - What fastText parameters did you use?
    -  How did you transform the review content?
    -  What else did you try and learn?