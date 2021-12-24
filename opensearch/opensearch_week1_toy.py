from opensearchpy import OpenSearch

host = 'localhost'
port = 9200
auth = ('admin', 'admin') # For testing only. Don't store credentials in code.

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
)

# Do a few checks before we start indexing:
client.cat.health()
client.cat.indices()

# If you still have your documents from the Dev Tools test, we should be able to check them here:
client.cat.count("searchml_test")