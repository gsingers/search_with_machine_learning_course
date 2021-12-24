mkdir -p /workspace/pyenv
pyenv install 3.9.7
mv /home/gitpod/.pyenv/versions/3.9.7/ /workspace/pyenv/versions/


mkdir -p /workspace/kaggle
touch /workspace/kaggle/kaggle.json
chmod 600 /workspace/kaggle/kaggle.json

curl -o logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz https://artifacts.opensearch.org/logstash/logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
tar -xf logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
cd docker
docker-compose pull
