from flask import g, current_app
from opensearchpy import OpenSearch

DEFAULT_HOST ='localhost'
DEFAULT_PORT = 9200
DEFAULT_AUTH = ('admin', 'admin')

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        g.opensearch = OpenSearch(
            hosts = [{'host': DEFAULT_HOST, 'port': DEFAULT_PORT}],
            http_compress = True,
            http_auth = DEFAULT_AUTH,
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
        )

    return g.opensearch
