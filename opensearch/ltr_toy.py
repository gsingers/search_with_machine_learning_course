from opensearchpy import OpenSearch
#
# Setup work
#


host = 'localhost'
port = 9200
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

# Create the client with SSL/TLS enabled, but hostname and certificate verification disabled.
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
# Add our sample document to the index.
docs = [
    {
        "id": "doc_a",
        "title": "Fox and Hounds",
        "body": "The quick red fox jumped over the lazy brown dogs.",
        "price": "5.99",
        "in_stock": True,
        "category": "childrens"},
    {
        "id": "doc_b",
        "title": "Fox wins championship",
        "body": "Wearing all red, the Fox jumped out to a lead in the race over the Dog.",
        "price": "15.13",
        "in_stock": True,
        "category": "sports"},
    {
        "id": "doc_c",
        "title": "Lead Paint Removal",
        "body": "All lead must be removed from the brown and red paint.",
        "price": "150.21",
        "in_stock": False,
        "category": "instructional"},
    {
        "id": "doc_d",
        "title": "The Three Little Pigs Revisted",
        "price": "3.51",
        "in_stock": True,
        "body": "The big, bad wolf huffed and puffed and blew the house down. The end.",
        "category": "childrens"}
]

# Create a new index
index_name = 'searchml_ltr'
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

# Turn on the LTR store and name it the same as our index
ltr_store_name = "_ltr/" + index_name

client.
