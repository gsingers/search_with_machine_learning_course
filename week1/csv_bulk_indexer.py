import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging
import time
import csv


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

def main(source_dir):
    start = time.time()
    index_name = 'bbuy_queries_using_python'
    client = get_opensearch()    
    docs_indexed = 0
    with open(source_dir, mode="r") as f:
        reader = csv.DictReader(f)
        docs = []
        for row in reader:
            doc = {
                "user": row["user"],
                "sku": row["sku"],
                "category": row["category"],
                "query": row["query"],
                "click_time": row["click_time"],
                "query_time": row["query_time"],
            }
            #print (row["user"])
            docs.append({'_index': index_name, '_id':doc['user'], '_source' : doc})
            #docs.append({'_index': index_name, '_source': doc})
            docs_indexed += 1
            if docs_indexed % 5000 == 0:
                bulk(client, docs, request_timeout=60)
                logger.info(f'{docs_indexed} documents indexed')
                docs = []
        if len(docs) > 0:
            bulk(client, docs, request_timeout=60)
            logger.info(f'{docs_indexed} documents indexed')
    process_time = time.time() - start
    logger.info(f'Done. Total docs: {docs_indexed} in {str(process_time)} seconds')
if __name__ == "__main__":
    src_dir=r'/workspace/datasets/train.csv'
    main(src_dir)
