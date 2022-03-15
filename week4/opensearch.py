from flask import g, current_app
from opensearchpy import OpenSearch


# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        # Load from config?
        host = 'localhost'
        port = 9200

        g.opensearch = OpenSearch(
            hosts=[{'host': host, 'port': port}]
        )

    return g.opensearch
