from flask import g, current_app
from opensearchpy import OpenSearch

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        # Load from config?
        host = 'localhost'
        port = 9200
        auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

        g.opensearch = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,  # enables gzip compression for request bodies
            http_auth=auth,
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl=True,
            verify_certs=False, # set to true if you have certs
            ssl_assert_hostname=False,
            ssl_show_warn=False,

        )

    return g.opensearch
