pyenv install 3.9.7
mkdir ~/.kaggle
pip install kaggle
curl -o logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz https://artifacts.opensearch.org/logstash/logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
tar -xf logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
cd docker
docker-compose pull
