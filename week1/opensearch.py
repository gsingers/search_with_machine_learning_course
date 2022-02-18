from flask import g, current_app
from opensearchpy import OpenSearch

def get_opensearch():
    if 'opensearch' not in g:
        host = 'localhost'
        port = 9200
        # totally ok here.
        auth = ('admin', 'admin')  

        g.opensearch = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,  
            http_auth=auth,
            use_ssl=True,
            verify_certs=False, 
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

    return g.opensearch
