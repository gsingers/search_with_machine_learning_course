# Implements various click models
import pandas as pd
import numpy as np

def binary_func(x):
    if x > 0:
        return 1
    return 0

def step(x):
    if x < 0.05: return 0
    elif x >= 0.05 and x < 0.10: return 0.5
    elif x >= 0.10 and x < 0.3: return 0.75
    else: return 1


# Given a click model type, transform the "grade" into an appropriate value between 0 and 1, inclusive
# This operates on the data frame and adds a "grade" column
#
def apply_click_model(data_frame, click_model_type="heuristic", downsample=True, prior=1000, alpha=30, beta=70, quantiles=10):
    if click_model_type == "binary":
        print("Binary click model")
        data_frame["grade"] = data_frame["clicks"].apply(lambda x: binary_func(x))
        if downsample:
            data_frame = down_sample_buckets(data_frame)
    elif click_model_type == "ctr":
        print("CTR click model")
        data_frame["grade"] = (data_frame["clicks"] / (data_frame["num_impressions"] + prior)).fillna(0)
        if downsample:
            data_frame = down_sample_continuous(data_frame)
    elif click_model_type == "beta":
        print("Beta click model")
        clicks_alpha = data_frame["clicks"] + alpha
        data_frame["grade"] = ((clicks_alpha) / ((data_frame["num_impressions"] + beta) + (clicks_alpha))).fillna(0)
        if downsample:
            data_frame = down_sample_continuous(data_frame)
    elif click_model_type == "quantiles": #similar to step, but quantiles
        print("CTR Quantiles click model")
        data_frame["grade"] = pd.qcut((data_frame["clicks"] / (data_frame["num_impressions"] + prior)).fillna(0), quantiles, labels=False) / quantiles
        if downsample:
            data_frame = down_sample_continuous(data_frame)
    elif click_model_type == "beta_quantiles": #similar to step, but quantiles
        print("Beta quantiles click model")
        clicks_alpha = data_frame["clicks"] + alpha
        data_frame["grade"] = pd.qcut(((clicks_alpha) / ((data_frame["num_impressions"] + beta) + (clicks_alpha))).fillna(0), quantiles, labels=False) / quantiles
        if downsample:
            data_frame = down_sample_continuous(data_frame)
    elif click_model_type == "heuristic":
        print("Heuristic click model")
        data_frame["grade"] = (data_frame["clicks"] / (data_frame["num_impressions"] + prior)).fillna(0).apply(lambda x: step(x))
        if downsample:
            #print("Size pre-downsample: %s\nVal Counts: %s\n" % (len(data_frame), data_frame['grade'].value_counts()))
            data_frame = down_sample_buckets(data_frame)
            #print("Size post-downsample: %s\nVal Counts: %s\n" % (len(data_frame), data_frame['grade'].value_counts()))
    return data_frame

# https://stackoverflow.com/questions/55119651/downsampling-for-more-than-2-classes
def down_sample_buckets(data_frame):
    g = data_frame.groupby('grade', group_keys=False)
    return pd.DataFrame(g.apply(lambda x: x.sample(g.size().min()))).reset_index(drop=True)


# Generate the probabilities for our grades and then use that to sample from
# from: https://stackoverflow.com/questions/63738389/pandas-sampling-from-a-dataframe-according-to-a-target-distribution
# If you want to learn more about this, see http://www.seas.ucla.edu/~vandenbe/236C/lectures/smoothing.pdf
def down_sample_continuous(data_frame):
    x = np.sort(data_frame['grade'])
    f_x = np.gradient(x)*np.exp(-x**2/2)
    sample_probs = f_x/np.sum(f_x)
    try: # if we have too many zeros, we can get value errors, so first try w/o replacement, then with
        sample = data_frame.sort_values('grade').sample(frac=0.8, weights=sample_probs, replace=False)
    except Exception as e:
        print("Unable to downsample, keeping original:\n%s" % e)
        sample = data_frame #data_frame.sort_values('grade').sample(frac=0.8, weights=sample_probs, replace=True)
    return sample

