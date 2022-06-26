import json

import requests


def create_rescore_ltr_query(user_query: str, query_obj, click_prior_query: str, ltr_model_name: str,
                             ltr_store_name: str,
                             active_features=None, # an array of strings
                             rescore_size=500, main_query_weight=1, rescore_query_weight=2):
    # Create the base query, use a much bigger window
    # add on the rescore
    ##### Step 4.e:
    query_obj["rescore"] = {
        "window_size": rescore_size,
        "query": {
            "rescore_query": {
                "sltr": {
                    "params": {
                        "keywords": user_query,
                        "click_prior_query": click_prior_query
                    },
                    "model": ltr_model_name,
                    "store": ltr_store_name
                }
            },
            "score_mode": "total",
            "query_weight": main_query_weight,
            "rescore_query_weight": rescore_query_weight
        }
    }

    if active_features is not None and len(active_features) > 0:
        query_obj["rescore"]["query"]["rescore_query"]["sltr"]["active_features"] =  active_features

    return query_obj


# take an existing query and add in an SLTR so we can use it for explains to see how much SLTR contributes
def create_sltr_simple_query(user_query, query_obj, click_prior_query, ltr_model_name, ltr_store_name, active_features=None):
    # Create the base query, use a much bigger window
    #add on the rescore
    sltr = {
        "sltr": {
            "params": {
                "keywords": user_query,
                "click_prior_query": click_prior_query
            },
            "model": ltr_model_name,
            # Since we are using a named store, as opposed to simply '_ltr', we need to pass it in
            "store": ltr_store_name,
        }
    }
    if active_features is not None and len(active_features) > 0:
        sltr["active_features"] =  active_features
    query_obj["query"]["bool"]["should"].append(sltr)
    return query_obj, len(query_obj["query"]["bool"]["should"])

def create_sltr_hand_tuned_query(user_query, query_obj, click_prior_query, ltr_model_name, ltr_store_name, active_features=None):
    # Create the base query, use a much bigger window
    #add on the rescore
    sltr = {
        "sltr": {
            "params": {
                "keywords": user_query,
                "click_prior_query": click_prior_query
            },
            "model": ltr_model_name,
            # Since we are using a named store, as opposed to simply '_ltr', we need to pass it in
            "store": ltr_store_name,
        }
    }
    if active_features is not None and len(active_features) > 0:
        sltr["active_features"] =  active_features
    query_obj["query"]["function_score"]["query"]["bool"]["should"].append(sltr)
    return query_obj, len(query_obj["query"]["function_score"]["query"]["bool"]["should"])

def create_feature_log_query(query, doc_ids, click_prior_query, featureset_name, ltr_store_name, size=200, terms_field="_id"):
    ##### Step 3.b:
    query_obj = {
        'size': size,
        'query': {
            'bool': {
                "filter": [  # use a filter so that we don't actually score anything
                    {
                        "terms": {
                            terms_field: doc_ids
                        }
                    },
                    {  # use the LTR query bring in the LTR feature set
                        "sltr": {
                            "_name": "logged_featureset",
                            "featureset": featureset_name,
                            "store": ltr_store_name,
                            "params": {
                                "keywords": query
                            }
                        }
                    }
                ]
            }
        },
        # Turn on feature logging so that we get weights back for our features
        "ext": {
            "ltr_log": {
                "log_specs": {
                    "name": "log_entry",
                    "named_query": "logged_featureset"
                }
            }
        }
    }

    return query_obj


# Item is a Pandas namedtuple
def get_features(item, exclusions, col_names):
    features = {}
    for idx, f in enumerate(item):
        col_name = col_names[idx]
        if col_name not in exclusions:
            # add it to the features
            # Do we also have a normalized version?  If so, skip this one, else add.
            # if we do have a normalized one, add it, but name it w/o the norm here so that it matches our featureset in LTR
            # there probably is a better way of doing this ^^
            normed = "%s_norm" % col_name
            if normed not in col_names:
                features[col_name.replace('_norm', '')] = f
    return features

def to_xgb_format(qid, doc_id, rank, query_str, product_name, grade, features):
    if features is not None:
        featuresAsStrs = ["%s:%.4f" % (idx + 1, feature) for idx, feature in enumerate(features.values())]
    else:
        featuresAsStrs = ""
    comment = "# %s\t%s\t%s\t%s" % (doc_id, rank, query_str, product_name)
    return "%.4f\tqid:%s\t%s %s" % (grade, qid, "\t".join(featuresAsStrs), comment.replace('\n',''))


def write_training_file(train_data, output_file, feat_map):
    print("Writing XGB Training file to %s" % (output_file))
    col_names = train_data.keys()
    # We don't want to write everything out, some items we've been tracking are reserved or not needed for the model
    exclusions = {"query_id", "doc_id", "rank", "query", "sku", "product_name", "grade", "clicks", "num_impressions"}
    with open(output_file, 'bw') as output:
        for item in train_data.itertuples(index=False): # skip the first 'index' element from the DF
            # Pull out the specific items from the Pandas named tuple.  The rest goes in the features map.
            # if there is a norm version, take that
            #
            features = get_features(item, exclusions, col_names)
            xgb_format = to_xgb_format(item.query_id, item.doc_id, item.rank, item.query,
                                           item.product_name, item.grade, features)
            output.write(bytes(xgb_format + "\n", 'utf-8'))
    # We need to write out the feature map, probably more needed here
    if feat_map:
        print("Writing feature map to %s" % feat_map)
        with open(feat_map, 'w') as feat_map_file:
            item = train_data.iloc[1:2]
            features = get_features(item, exclusions, col_names)
            feat_map_file.write("0\tna\tq\n")
            for idx, feat in enumerate(features.keys()):
                #https://docs.rs/xgboost/0.1.4/xgboost/struct.FeatureMap.html are the only docs I can find on the format
                if feat != "onSale":
                    feat_map_file.write('{}\t{}\tq\n'.format(idx+1,feat))#idx+2 b/c we are one-based for this
                else: #Kludgy way of handling onSale being at some point.  For now, write it out as 'q'
                    # Bug in LTR prevents 'indicator'/boolean features, so model as q for now by
                    # encoding onSale as a percentage discount
                    feat_map_file.write('{}\t{}\tq\n'.format(idx+1,feat)) #make the q an i




def write_opensearch_ltr_model(model_name, model, model_file, objective="rank:pairwise"):
    model_str = '[' + ','.join(list(model)) + ']'
    #print(model_str)
    os_model = {
            "model": {
                "name": model_name,
                "model": {
                    "type": "model/xgboost+json",
                    "definition": '{"objective":"%s", "splits": %s}' % (objective, model_str)
                }
            }
        }
    print("Saving XGB LTR-ready model to %s.ltr" % model_file)
    with open("%s.ltr" % model_file, 'w') as ltr_model:
        ltr_model.write(json.dumps(os_model))



def create_ltr_store(ltr_model_path, auth, delete_old=True):
    if delete_old:
        resp = requests.delete(ltr_model_path, auth=auth, verify=False)
        print("Deleted old store response status: %s" % resp.status_code)
    # Create our new LTR storage
    resp = requests.put(ltr_model_path, auth=auth, verify=False)
    print("Create the new store at %s response status: %s" % (ltr_model_path, resp.status_code))
    return resp


def post_featureset(featureset_path, ltr_feature_set, auth, headers={"Content-Type": 'application/json'}):
    print("POSTing the featureset to %s" % (featureset_path))
    resp = requests.post(featureset_path, headers=headers, data=json.dumps(ltr_feature_set), auth=auth, verify=False)
    return resp


def delete_model(model_path, auth):
    print("Deleting model from %s" % model_path)
    response = requests.delete(model_path, auth=auth, verify=False)
    print("\tDelete Model Response: %s: %s" % (response.status_code, response.text))
    return response

def upload_model(model_path, os_model, auth):
    print("Uploading model to %s" % model_path)
    headers = {"Content-Type": 'application/json'}
    response = requests.post(model_path, data=json.dumps(os_model), headers=headers, auth=auth, verify=False)
    print("\tUpload Model Response: %s: %s" % (response.status_code, response.text))
    return response