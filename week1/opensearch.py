#!/usr/bin/env python

"""The `opensearch.py` module defines the `get_opensearch()` function
that creates an OpenSearch client instance, makes that client available
in flask's global namespace `g` by setting `g.opensearch`, and returns
the OpenSearch client.

References:
> See opensearch-py docs:
> https://github.com/opensearch-project/opensearch-py
"""

import os
from flask import g, current_app
from opensearchpy import OpenSearch


HOST = 'localhost'
PORT = 9200

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:
        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        # g.opensearch = None

        # auth = (os.environ['OPENSEARCH_USERNAME'], os.environ['OPENSEARCH_PW'])
        g.opensearch = None


    return g.opensearch
