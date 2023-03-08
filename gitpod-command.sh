ln -s /workspace/kaggle/ /home/gitpod/.kaggle

mkdir -p /workspace/opensearch
mkdir -p /workspace/datasets

# If we want OpenSearch to be able to put the data here we have to give
# filesystem permissions to the UID/GID that OpenSearch is running as
# inside its container.
sudo chown -R 1000:1000 /workspace/opensearch

mkdir /workspace/ltr_output
cp data/validity.csv /workspace/ltr_output/

cd docker
docker-compose up -d

cd /home/gitpod/fastText-0.9.2 && /usr/bin/make -f /home/gitpod/fastText-0.9.2/Makefile clean fasttext
