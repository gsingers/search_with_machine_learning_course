import opensearchpy
import requests
from lxml import etree

import click
import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# NOTE: this is not a complete list of fields.  If you wish to add more, put in the appropriate XPath expression.
# TODO: is there a way to do this using XPath/XSL Functions so that we don't have to maintain a big list?
mappings = [
    "productId/text()", "productId",
    "sku/text()", "sku",
    "name/text()", "name",
    "type/text()", "type",
    "startDate/text()", "startDate",
    "active/text()", "active",
    "regularPrice/text()", "regularPrice",
    "salePrice/text()", "salePrice",
    "onSale/text()", "onSale",
    "digital/text()", "digital",
    "frequentlyPurchasedWith/*/text()", "frequentlyPurchasedWith",  # Note the match all here to get the subfields
    "accessories/*/text()", "accessories",  # Note the match all here to get the subfields
    "relatedProducts/*/text()", "relatedProducts",  # Note the match all here to get the subfields
    "crossSell/text()", "crossSell",
    "salesRankShortTerm/text()", "salesRankShortTerm",
    "salesRankMediumTerm/text()", "salesRankMediumTerm",
    "salesRankLongTerm/text()", "salesRankLongTerm",
    "bestSellingRank/text()", "bestSellingRank",
    "url/text()", "url",
    "categoryPath/*/name/text()", "categoryPath",  # Note the match all here to get the subfields
    "categoryPath/*/id/text()", "categoryPathIds",  # Note the match all here to get the subfields
    "categoryPath/category[last()]/id/text()", "categoryLeaf",
    "count(categoryPath/*/name)", "categoryPathCount",
    "customerReviewCount/text()", "customerReviewCount",
    "customerReviewAverage/text()", "customerReviewAverage",
    "inStoreAvailability/text()", "inStoreAvailability",
    "onlineAvailability/text()", "onlineAvailability",
    "releaseDate/text()", "releaseDate",
    "shippingCost/text()", "shippingCost",
    "shortDescription/text()", "shortDescription",
    "shortDescriptionHtml/text()", "shortDescriptionHtml",
    "class/text()", "class",
    "classId/text()", "classId",
    "subclass/text()", "subclass",
    "subclassId/text()", "subclassId",
    "department/text()", "department",
    "departmentId/text()", "departmentId",
    "bestBuyItemId/text()", "bestBuyItemId",
    "description/text()", "description",
    "manufacturer/text()", "manufacturer",
    "modelNumber/text()", "modelNumber",
    "image/text()", "image",
    "condition/text()", "condition",
    "inStorePickup/text()", "inStorePickup",
    "homeDelivery/text()", "homeDelivery",
    "quantityLimit/text()", "quantityLimit",
    "color/text()", "color",
    "depth/text()", "depth",
    "height/text()", "height",
    "weight/text()", "weight",
    "shippingWeight/text()", "shippingWeight",
    "width/text()", "width",
    "longDescription/text()", "longDescription",
    "longDescriptionHtml/text()", "longDescriptionHtml",
    "features/*/text()", "features"  # Note the match all here to get the subfields

]


def get_opensearch():
    host = 'localhost'
    port = 9200
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,
        use_ssl=False,
    )
    return client


def main(source_dir):
    index_name = 'bbuy_products'
    client = get_opensearch()
    files = glob.glob(source_dir + "/*.xml")
    docs_indexed = 0
    for file in files:
        logger.info(f'Processing file : {file}')
        tree = etree.parse(file)
        root = tree.getroot()
        children = root.findall("./product")
        docs = []
        for child in children:
            doc = {}
            for idx in range(0, len(mappings), 2):
                xpath_expr = mappings[idx]
                key = mappings[idx + 1]
                doc[key] = child.xpath(xpath_expr)
            # print(doc)
            if not 'productId' in doc or len(doc['productId']) == 0:
                continue

            docs.append({'_index': index_name, '_id': doc['sku'][0], '_source': doc})
            # docs.append({'_index': index_name, '_source': doc})
            docs_indexed += 1
            if docs_indexed % 200 == 0:
                bulk(client, docs, request_timeout=60)
                logger.info(f'{docs_indexed} documents indexed')
                docs = []
        if len(docs) > 0:
            bulk(client, docs, request_timeout=60)
            logger.info(f'{docs_indexed} documents indexed')
    logger.info(f'Done. Total docs: {docs_indexed}')


if __name__ == "__main__":
    main('data/product_data/products')
