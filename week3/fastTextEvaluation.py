import fasttext

model = fasttext.load_model('titles_model')

test_tokens = [
'camera',
'player',
'printer',
'mouse',
'dvd',
'camcorder',
'card',
'macbook',
'ipod',
'screen',
'memory',
'laptop',
'amplifier',
'speaker',
'headphone',
'green',
'blue',
'pink',
'nintendo',
'pioneer',
'oven',
'toshiba']

threshold = 0.25

for token in test_tokens:
    neighbours = model.get_nearest_neighbors(token)
    print(f'### {token}')
    print(' ')
    for n in neighbours:
        if n[0] > threshold:
            print(n[1])
    print('\n')