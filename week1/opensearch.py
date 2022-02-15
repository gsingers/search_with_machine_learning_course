from flask import g, current_app
from opensearchpy import OpenSearch

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        g.opensearch =  OpenSearch(
            'https://localhost:9200',
            http_auth = ('admin', 'admin'),
            ssl_show_warn = False,
            # turn on SSL
            use_ssl=False,
            # make sure we verify SSL certificates
            verify_certs=False
        )

    return g.opensearch
