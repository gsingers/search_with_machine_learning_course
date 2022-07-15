# Useful Commands


### Activate environment:

`pyenv activate search_with_ml`

### Run LTR end to end script

`./ltr-end-to-end.sh -y`

#### With quantiles click model

`./ltr-end-to-end.sh -y -m 0 -c quantiles`

### Open up model tree & model importance diagrams

`open /workspace/ltr_output/ltr_model_tree.png`

`open /workspace/ltr_output/ltr_model_importance.png`

### Debug with ipython

Add the following to your python code:

```python
q = __import__("functools").partial(__import__("os")._exit, 0)  # FIXME
__import__("IPython").embed() 
```

### Dev tools link

[https://5601-sleepypione-searchwithm-f1dtrg60foq.ws-eu53.gitpod.io/app/dev_tools#/console](https://5601-sleepypione-searchwithm-f1dtrg60foq.ws-eu53.gitpod.io/app/dev_tools#/console)
[https://5601-sleepypione-searchwithm-f1dtrg60foq.ws-eu54.gitpod.io/app/home#/](https://5601-sleepypione-searchwithm-f1dtrg60foq.ws-eu54.gitpod.io/app/home#/)
