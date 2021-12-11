
mkdir -p /workspace/opensearch
mkdir -p /workspace/logstash
mkdir -p /workspace/datasets
sudo chown -R gitpod:gitpod /workspace/opensearch
sudo  chown -R gitpod:gitpod /workspace/logstash
cd docker
docker-compose up -d