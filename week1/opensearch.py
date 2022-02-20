from flask import g, current_app
from opensearchpy import OpenSearch
import json
host = 'localhost'
port = 9200
auth = ('admin', 'admin')

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True, 
            http_auth = auth,
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
        )

        g.opensearch = client

    return g.opensearch
