#!/usr/bin/env bash
#
# Setup the class environment
#
# Pre-requisites:
# . python 3.9.7
# . homebrew
#
# . Download and place kaggle.json into ~/.kaggle/
#
#
set -e


cd $(dirname $0)
source ./sml-config.sh


echo "------------------------------------------------------------------------"
echo ":: creating workspace: ${workspace}"
echo "------------------------------------------------------------------------"
mkdir -p ${workspace}

# docker bind mount for opensearch data persistence
mkdir -p ${workspace}/docker-data/opensearch/data

# docker bind mount of workspace for logstash
mkdir -p ${workspace}/logstash/

# cp logstash configs into workspace to make them accessible to containers
cp ${repo}/logstash/index-bbuy.logstash ${workspace}/logstash/
cp ${repo}/logstash/index-bbuy-queries.logstash ${workspace}/logstash/

# change the opensearch host name to match the docker node
perl -pi -e 's/localhost/opensearch-node1/g' ${workspace}/logstash/index-bbuy*logstash


echo "------------------------------------------------------------------------"
echo ":: installing pre-reqs"
echo "------------------------------------------------------------------------"
brew install fasttext


echo "------------------------------------------------------------------------"
echo ":: setting up python virtual env"
echo "------------------------------------------------------------------------"
python3 -m venv .venv
source .venv/bin/activate
python3.9 -m pip install --upgrade pip
pip install -r ./requirements.txt


echo "------------------------------------------------------------------------"
echo ":: setting up and downloading datasets from kaggle"
echo "------------------------------------------------------------------------"
if [[ ! -f ${workspace}/datasets/acm-sf-chapter-hackathon-big.zip ]]; then
    ls -al ~/.kaggle/kaggle.json
    mkdir -p ${workspace}/datasets/
    cd ${workspace}/datasets/
    kaggle competitions download -c acm-sf-chapter-hackathon-big
    unzip acm-sf-chapter-hackathon-big.zip
    tar -xf product_data.tar.gz
fi


echo "------------------------------------------------------------------------"
echo ":: done!"
echo "------------------------------------------------------------------------"
