# Welcome to Search with Machine Learning

Search with Machine Learning is a four week class taught by Grant Ingersoll and Daniel Tunkelang and is focused on helping students
quickly get up to speed on search best practices by first teaching the basics of search and then extending those basics with machine learning.  

Students will learn indexing, querying, aggregations and text analysis, as well as how to use machine learning for ranking, content classification and query understanding.

The class is a hands-on project-driven course where students will work with real data and the [Opensearch](https://opensearch.com)/Elasticsearch ecosystem along with libraries like [FastText](https://fasttext.cc/)

# Class code layout (e.g. where the projects are)

For our class, we have four weekly projects.  Each project
is a standalone Python Flask application that interacts with an OpenSearch server (and perhaps other services).  

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

*NOTE*: The Gitpod free tier comes with 50 hours of use per month.  We expect our work will be done in less time than that.  HOwever, you may wish to conserve time on the platform by being sure to stop your workspace when you are done with it.  Gitpod will time you out (don't worry, you're work will be saved), but that may take longer to detect.

The following things must be done each time you create a new Gitpod Workspace (unfortunately, we can't automate this)

1. Fork this repository.
1. Launch a new Gitpod workspace based on this repository.
1. Install (create/copy) your Kaggle API token in `~/.kaggle/kaggle.json`
1. Run the download data script:

        ./download-data.sh
        
1. You should now have a running Opensearch instance (port 9200) and a running Opensearch Dashboards instance (port 5601)
1. Login to the dashboards and change your password to something you will remember, as these are public instances.  



# Working locally (Not supported, but may work for you. YMMV)     

# Running an example

At the command line, do the following steps to run the example.  For purposes of demonstration, let's assume we are working on week 2.  Substitute accordingly for the week you are working on.

1. Setup your Python Virtual Environment.  We use `pyenv` (Pyenv website)[https://github.com/pyenv/pyenv] and `pyenv-virtualenv` (Pyenv Virtualenv)[https://github.com/pyenv/pyenv-virtualenv], but you can use whatever you are most comfortable with.
    1. `pyenv install 3.9.7` -- Install Python 3.9.7 into PyEnv
    1. `pyenv virtualenv 3.9.7 search_with_ml_week2` -- Create a Virtualenv using that 3.9.7 install
    1. `pyenv activate search_with_ml_week2` -- Activate that Virtualenv. 
1. Install the Python dependencies: `pip install -r requirements_week2.txt`
1. Run Flask: 
    1. `export FLASK_ENV=development`
    1.  *_IMPORTANT_* Set the Flask App Environment Variable: `export FLASK_APP=week1` 
    1. `flask run --port 3000` (The default port of 5000 is already in use) 