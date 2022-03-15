import fasttext

queries = ['ipad 2', 'smartphone new 128GB', 'printer epson', '']
def print_results(N, p, r, k):
    print("N\t" + str(N))
    print("P@{}\t{:.3f}".format(k, p))
    print("R@{}\t{:.3f}".format(k, r))


def test_models():
    for min_queries in [25, 50, 100, 500, 1000, 2000, 5000]:
        print(min_queries)
        print('*****')
        model = fasttext.load_model(f'queries_classification_model_{min_queries}.bin')
        for k in [1, 3, 5]:
            N, precision, recall = model.test(f'queries_test_{min_queries}', k=k)
            print_results(N, precision, recall, k)
        del model


if __name__ == '__main__':
    test_models()

