import fasttext

queries = ['ipad 2', 'smartphone new 128GB', 'printer epson', 'iphone', 'pokemon', 'video game',
           'blue sunshine CD', 'dvd blue-ray', 'laptop']


def print_results(r, k):
    print("R@{}\t{:.3f}".format(k, r))


def test_models():
    for min_queries in [25, 50, 100, 500, 1000, 2000, 5000]:
        print(f'#### Min Queries: {min_queries}')
        model = fasttext.load_model(f'queries_classification_model_{min_queries}.bin')

        for k in [1, 3, 5]:
            N, precision, recall = model.test(f'queries_test_{min_queries}', k=k)
            print_results(recall, k)
        print('')
        for query in queries:
            prediction = model.predict(query, threshold=0.8)
            prediction = dict(zip(prediction[0], prediction[1]))

            if prediction.keys():
                predictions = [p.removeprefix('__label__') for p in prediction.keys()]
                predictions = ", ".join(predictions)
                print(f'Prediction for {query}: {predictions}')
        print('')
        del model


if __name__ == '__main__':
    test_models()
