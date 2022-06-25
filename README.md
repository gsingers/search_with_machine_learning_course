# Welcome to Search with Machine Learning

Search with Machine Learning is a four week class taught by Grant Ingersoll and Daniel Tunkelang and is focused on helping students
quickly get up to speed on search best practices by first teaching the basics of search and then extending those basics with machine learning.  

Students will learn indexing, querying, aggregations and text analysis, as well as how to use machine learning for ranking, content classification and query understanding.

The class is a hands-on project-driven course where students will work with real data and the [Opensearch](https://opensearch.com)/Elasticsearch ecosystem along with libraries like [FastText](https://fasttext.cc/), [XG Boost](https://xgboost.readthedocs.io/en/stable/) and [OpenSearch Learning to Rank](https://github.com/aparo/opensearch-learning-to-rank).

# Class code layout (e.g. where the projects are)

For our class, we have four weekly projects.  Each project
is a standalone Python application that interacts with an OpenSearch server (and perhaps other services).  

You will find these four projects in the directories below them organized in the following way:

- Week 1:
    - week1 -- The unfinished template for the week's project, annotated with instructions.
- Week 2:
    - week2 -- The unfinished template for the week's project, annotated with instructions.
- Week 3 and 4: you get the picture

Our instructor annotated results for each project will be provided during the class.  Please note, these represent our way of doing the assignment and may differ from your results, as there is often more than one way of doing things in search.

You will also find several supporting directories and files for [Logstash](https://opensearch.org/docs/latest/clients/logstash/), Docker and Gitpod.

# Prerequisites

1. For this class, you will need a Kaggle account and a [Kaggle API token](https://www.kaggle.com/docs/api).
1. No prior search knowledge is required, but you should be able to code in Python or Java (all examples are in Python)
1. You will need a [Gitpod](https://gitpod.io) account.

# Working in Gitpod (Officially Supported)

*NOTE*: The Gitpod free tier comes with 50 hours of use per month.  We expect our work will be done in less time than that.  However, you may wish to conserve time on the platform by being sure to stop your workspace when you are done with it.  Gitpod will time you out (don't worry, your work will be saved), but that may take longer to detect.

The following things must be done each time you create a new Gitpod Workspace (unfortunately, we can't automate this)

1. Fork this repository.
1. Launch a new Gitpod workspace based on this repository.  This will automatically start OpenSearch and OpenSearch Dashboards.
    1. Note: it can take a few minutes for OpenSearch and the dashboards to launch.        
1. You should now have a running Opensearch instance (port 9200) and a running Opensearch Dashboards instance (port 5601)
1. Login to the dashboards at `https://5601-<$GITPOD_URL>/` with default username `admin` and password `admin`. Change your password to something you will remember, as these are public instances.  This should popup automatically as a new tab, unless you have blocked popups.

        $GITPOD_URL is a placeholder for your ephemeral Gitpod host name, e.g. silver-grasshopper-8czadqyn.ws-us25.gitpod.io     

# Downloading the Best Buy Dataset

1. Run the install [Kaggle API token](https://www.kaggle.com/docs/api) script and follow the instructions:

        ./install-kaggle-token.sh
1. Accept all of the [kaggle competition rules](https://www.kaggle.com/c/acm-sf-chapter-hackathon-big/rules) then run the download data script:

        ./download-data.sh



# Exploring the OpenSearch Sample Dashboards and Data

1. Login to OpenSearch and point your browser at `https://5601-<$GITPOD_URL>/app/opensearch_dashboards_overview#/`
1. Click the "Add sample data" link
1. Click the "Add Data" link for any of the 3 projects listed. In the class, we chose the "Sample flight data", but any of the three are fine for exploration.

# Running the Weekly Project

At the command line, do the following steps to run the example.  

1. Activate your Python Virtual Environment.  We use `pyenv` (Pyenv website)[https://github.com/pyenv/pyenv] and `pyenv-virtualenv` (Pyenv Virtualenv)[https://github.com/pyenv/pyenv-virtualenv].
    1. `pyenv activate search_with_ml` -- Activate the Virtualenv. 
1. Run Flask: 
    1. `export FLASK_ENV=development`
    1.  *_IMPORTANT_* Set the Flask App Environment Variable: `export FLASK_APP=week2`
    1. For week2, you may also choose to set `export PRIOR_CLICKS_LOC=/workspace/ltr_output/train.csv` after running the LTR end-to-end script. 
    1. `flask run --port 3000` (The default port of 5000 is already in use) 
    1. Open the Flask APP at `https://3000-<$GITPOD_URL>/`
1. Or run `ipython`
    
# Working locally (Not supported, but may work for you. YMMV)

To run locally, you will need a few things:

1. [Pyenv](https://github.com/pyenv/pyenv) and [Pyenv-Virtualenv](https://github.com/pyenv/pyenv-virtualenv) with Python 3.9.7 installed
1. [Docker](https://docker.com/)
1. A [Git](https://git-scm.com/) client

Note: these have only been tested on a Mac running OS 12.2.1.  YMMV.  Much of what you will need to do will be similar to what's in `.gitpod.Dockerfile`

1.  Install [GraphViz](https://www.graphviz.org/)
1. `pyenv install 3.9.7`
1. `pip install` all of the libraries you see in `.gitpod.Dockerfile`
1. Setup your weekly python environments per the "Weekly Project" above.
1. Install [Fasttext](https://fasttext.cc/)  
1. Run OpenSearch: 
    1. `cd docker`
    1. `docker-compose up`
1. Note: most of the scripts and projects assume the data is in `/workspace/datasets`, but have overrides to specify your own directories. You will need to download and plan accordingly.  
1. Do your work per the Weekly Project     
    