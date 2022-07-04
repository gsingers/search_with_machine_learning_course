from opensearchpy import OpenSearch
from pprint import pprint

host = 'localhost'

host = 'localhost'
port = 9200
base_url = "https://{}:{}/".format(host, port)
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
index_name = "bbuy_products"
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


query = {"query": {"bool": {"filter": [{"terms": {"_id": [9448216, 9448234, 9956028]}}, {"sltr": {"_name": "logged_featureset", "featureset": "bbuy_main_featureset",
                                                                                                  "store": "week1", "params": {"keywords": "zune"}}}]}}, "ext": {"ltr_log": {"log_specs": {"name": "log_entry", "named_query": "logged_featureset"}}}}

response = client.search(query, index_name)

hits = response['hits']['hits']

for hit in hits:
    hit

# from toy example
client.search({}, 'searchml_ltr')

pprint(client.indices.get_mapping('searchml_ltr'))

client.search()

index_name = 'search_fun_revisited_custom_mappings'
index_body = {
    'settings': {
        'index': {
            'query': {
                'default_field': "body"
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "english"},
            "body": {"type": "text", "analyzer": "english"},
            "in_stock": {"type": "boolean"},
            "category": {"type": "keyword", "ignore_above": "256"},
            "price": {"type": "float"}
        }
    }
}

client.indices.create(index_name, body=index_body)

client.search({},'search_fun_revisited_custom_mappings')

