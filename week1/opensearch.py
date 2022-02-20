from flask import g, current_app
from opensearchpy import OpenSearch
host = 'localhost'
port = 9200
auth = ('admin', 'admin') # For testing only. Don't store credentials in code.
#ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.
# Create an OpenSearch client instance and put it into Flask shared space for use by the application

# Optional client certificates if you don't want to use HTTP basic authentication.
# client_cert_path = '/full/path/to/client.pem'
# client_key_path = '/full/path/to/client-key.pem'

def get_opensearch():
    if 'opensearch' not in g:
        # Client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = auth,
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl = True,
            verify_certs = True,
            ssl_assert_hostname = False,
            ssl_show_warn = False
            #ca_certs = ca_certs_path
        )
        g.opensearch = client

    return g.opensearch
