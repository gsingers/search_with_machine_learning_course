# Answers for Week 3

## Link to your Gitpod/Github repo 

https://github.com/snikoyo/search_with_machine_learning_course

Branch: my-week-3

## 1. For classifying product names to categories:

### a. What precision (P@1) were you able to achieve?

P@1     0.656
R@1     0.656

### b. What fastText parameters did you use?

` -lr 1.0  -epoch 25 -wordNgrams 2 -maxn 0 -minn 0`

There was virtually no difference between 1, 2 and 3 wordNgrams.

### c. How did you transform the product names?

First, I removed the duplicate product names (there were over 20000 of them) using `sort | uniq | shuf > output.fasttext`.
Then I tokenized and stemmed them (the stemmer also lowercased), using NLTK and the Porter Stemmer:

       words = word_tokenize(product_name)
       words = [ps.stem(w) for w in words]
    
       product_name_transformed = ' '.join(words) 

In a second try, I did not stem, just lower case, remove numbers and punctuation and any trailing s.
I got 0.66 P1 in this try, so the Porter Stemmer either is not very good or stemming does not help much with this task. 

Also, I used 20000 product names instead of 10000 in the training set. 

### d. How did you prune infrequent category labels, and how did that affect your precision?

## 2. For deriving synonyms from content:

### a. What 20 tokens did you use for evaluation?

See Evaluation.

### b. What fastText parameters did you use?

lr=0.2, epoch=40, minCount=50, verbose=2, minn=0, maxn=0, wordNgrams=2, dim=200, ws=3, loss='ns
The sample rate was 0.2.

### c. How did you transform the product names?

Similar to the first task - lower case, remove numbers and punctuation- but without removing trailing s. 

### d. What threshold score did you use?

0.25

### e. What synonyms did you obtain for those tokens?
#### camera
 
megapixel

cameras

zoom

nikon

lens

slr

digital

rebel

dslr

eos



#### player
 
receiver

dvd

deck

recorder

ray

blu

definition

hdtv

radio

disc



#### printer
 
copier

brother

inkjet

scanner

cartridge

epson

photo

gateway

desktop

color



#### mouse
 
optical

savings

notebook

backpack

targus

texas

laptop

netbook

sleeve

call



#### dvd
 
disc

ray

player

blu

recorder

deck

insignia

definition

widescreen

video



#### camcorder
 
tripod

definition

powershot

jvc

camera

easyshare

slr

kodak

rebel

extra



#### macbook
 
air

targus

htc

ipad

laptop

iphone

generation

toshiba

acer

laptops



#### ipod
 
apple

radio

nano

generation

earbuds

iphone

ipad

players

griffin

earbud



#### screen
 
protector

touch

zagg

widescreen

invisibleshield

player

earbuds

ipod

griffin

lcd



#### memory
 
drive

amd

intel

megapixel

hard

camcorder

laptop

duo

card

processor



#### laptop
 
notebook

netbook

core

processor

savings

desktop

amd

intel

computer

atom



#### amplifier
 
kicker

hdtv

mosfet

radio

class

bass

watt

pedal

scosche

signature



#### speaker
 
speakers

pair

audio

radio

each

sound

shelf

subwoofer

dock

yamaha



#### green
 
red

blue

pink

purple

orange

silver

audioquest

san

skullcandy

generation



#### blue
 
red

pink

silver

green

orange

purple

gray

case

brown

white



#### pink
 
blue

purple

green

red

skin

case

jacket

silver

generation

gray



#### nintendo
 
wii

xbox

playstation

gamecube

psp

wars

advance

boy

bundle

game



#### pioneer
 
kenwood

mosfet

kicker

jvc

audio

radio

receiver

ready

deck

marine



#### oven
 
convection

cooktop

freestanding

self

range

microwave

cleaning

slide

stainless

steel



#### toshiba
 
acer

compaq

inspiron

dell

pavilion

samsung

lenovo

asus

gateway

sony
