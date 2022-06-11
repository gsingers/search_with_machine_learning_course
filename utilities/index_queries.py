# From Dmitiriy Shvadskiy https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_queries.py
import click
import pandas as pd
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

def get_opensearch():

    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')
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
        #ca_certs=ca_certs_path
    )
    return client

@click.command()
@click.option('--source_file', '-s', help='source csv file', required=True)
def main(source_file):
    index_name = 'bbuy_queries'
    client = get_opensearch()
    ds = pd.read_csv(source_file)
    #print(ds.columns)
    ds['click_time'] = pd.to_datetime(ds['click_time'])
    ds['query_time'] = pd.to_datetime(ds['query_time'])
    #print(ds.dtypes)
    docs = []
    for idx, row in ds.iterrows():
        doc = {}
        for col in ds.columns:
            doc[col] = row[col]
        docs.append({'_index': index_name , '_source': doc})
        if idx % 300 == 0:
            bulk(client, docs, request_timeout=60)
            logger.info(f'{idx} documents indexed')
            docs = []
    if len(docs) > 0:
        bulk(client, docs, request_timeout=60)
    logger.info(f'Done indexing {ds.shape[0]} records')

if __name__ == "__main__":
    main()