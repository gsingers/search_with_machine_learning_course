ln -s /workspace/kaggle /home/gitpod/.kaggle
ln -s /workspace/pyenv/versions/3.9.7 /home/gitpod/.pyenv/versions/3.9.7
mkdir -p /workspace/opensearch
mkdir -p /workspace/logstash
mkdir -p /workspace/datasets
sudo chown -R gitpod:gitpod /workspace/opensearch
sudo  chown -R gitpod:gitpod /workspace/logstash
cd docker
docker-compose up -d