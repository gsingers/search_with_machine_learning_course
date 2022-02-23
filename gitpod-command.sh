ln -s /workspace/kaggle /home/gitpod/.kaggle

mkdir -p /workspace/opensearch
mkdir -p /workspace/logstash
mkdir -p /workspace/datasets
sudo chown -R gitpod:gitpod /workspace/opensearch
sudo  chown -R gitpod:gitpod /workspace/logstash
ln -s /home/gitpod/logstash-7.13.2 /workspace/logstash/logstash-7.13.2


cd docker
docker-compose up -d

