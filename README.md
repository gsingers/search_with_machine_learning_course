# Welcome to Search with Machine Learning

If you are reading this, you are _almost_ in the right place.  For our class, we have four weekly projects.  Each project
is a standalone Python Flask application that interacts with an OpenSearch server (and perhaps other services).  

You will find these four projects in the directories below them organized in the following way:

- Week 1:
    - week1 -- The unfinished template for the week's project, annotated with instructions.
- Week 2:
    - week2 -- The unfinished template for the week's project, annotated with instructions.
- Week 3 and 4: you get the picture
    

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
    1. `flask run`  