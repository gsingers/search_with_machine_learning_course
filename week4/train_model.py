import fasttext


# loss function {ns, hs, softmax, ova}
if __name__ == '__main__':

    for min_queries in [25, 50, 100, 500, 1000, 2000, 5000]:
        print(min_queries)
        print('*****')
        model = fasttext.train_supervised(input=f"queries_train_{min_queries}",
                                          lr=0.2, epoch=50, seed=min_queries,
                                          minn=4, maxn=8, wordNgrams=2)

        model.save_model(f'queries_classification_model_{min_queries}.bin')
        # warum bekomme ich immer dieselben Ergebnisse?
        del model
