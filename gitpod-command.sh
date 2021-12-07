mkdir -p /workspace/opensearch
mkdir -p /workspace/logstash
sudo chown -R gitpod:gitpod /workspace/opensearch
sudo chown -R gitpod:gitpod /workspace/opensearch-data1
sudo  chown -R gitpod:gitpod /workspace/logstash
cd docker
docker-compose up -d