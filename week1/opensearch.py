from flask import g, current_app
from opensearchpy import OpenSearch

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        auth = ('admin', 'admin')
        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        g.opensearch = OpenSearch(
            hosts = [{'host': 'localhost', 'port': 9200}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = auth,
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl = True,
            verify_certs = False,
            #ssl_assert_hostname = False,
            ssl_show_warn = False,
            #ca_certs = ca_certs_path
        )

    return g.opensearch
