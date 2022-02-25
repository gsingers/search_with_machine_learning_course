

## Local SML development on OS X with docker

This is a small collection of utilities to help support running the 
search-with-ml (sml) environment locally on OS X. It is derived from the main
repo utils and various references in slack. It attempts to mimic the gitpod
workspace and other conventions as closely as possible to stay aligned with
project instructions and logstash config files.


Pre-requisites:
* Generally assumes OS X but most of it is also linux compatible
* Docker, including docker compose
* python 3.9.7
* homebrew (for fasttext. optional?)
* Assumes some familiarity with docker, bash cli, etc


## (1) Initial Setup

The setup process is similar to the gitpod setup.  However, note that it
replaces install-kaggle-token.sh, download-data.sh, gitpod*, .gitpod*, pyenv.


### (1a) initial manual steps required:

* Download and place kaggle.json into ~/.kaggle/ for access to the kaggle api
* edit ./sml-config.sh: add your own desired workspace path (ex: ~/corise-sml/)
* edit ./sml-config.sh: add the path to your sml repo


### (1b) one time setup, semi-automated:

See script for details. This gets data, sets up workspace, docker data, etc.

```
> cd ${repo}/localdev-osx/
> ./sml-init.sh
```


### (1c) mimic /workspace

Many of the class files hard code the workspace directory (/workspace/...) in
to various paths. However, this localdev system uses a workspace in your home
directory, such as `~/corise-sml/`.

One solution is to just edit those files as you come across them. Another solution
is to symlink /workspace to your own workspace directory, but doing that is a
little odd in modern OS X.  Here is a lead on how to do so:

* https://stackoverflow.com/questions/58396821/what-is-the-proper-way-to-create-a-root-sym-link-in-catalina



## (2) Running services, loading docs, and ongoing dev work

This section illustrates how this can be used for sml dev work. Those skilled 
in the art can of course detach containers and orchestrate work in various 
other ways as desired.


### terminal 1 (opensearch):

This starts up containers for opensearch and the opensearch dashboard.

```
> cd ${repo}/localdev-osx/
> docker compose up opensearch-node1 opensearch-dashboards
```


### terminal 2 (logstash):

This adds schema, starts up logstash in containers, and loads the documents

```
> cd ${repo}/localdev-osx/
> ./sml-load-schema.sh
> docker compose up logstash-products logstash-queries
```

### terminal 3 (flask):

Run flask

```
> cd ${repo}/
> source ./localdev-osx/.venv/bin/activate
> export FLASK_ENV=development
> export FLASK_APP=week2
> flask run --port 3000
```


### terminal 4 (dev):

Do whatever

```
# head to the repo and activate the py virtual env
> cd ${repo}/
> source ./localdev-osx/.venv/bin/activate

# run whatever commands
> ./count-tracker.sh
> ./delete-indexes.sh
> vim week2/search.py
> curl -k -s -X GET -u admin https://localhost:9200/bbuy_products/_count | jq .
> etc...
```





