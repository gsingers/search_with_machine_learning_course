ln -s /workspace/kaggle /home/gitpod/.kaggle
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
mkdir -p /workspace/opensearch
mkdir -p /workspace/logstash
mkdir -p /workspace/datasets
sudo chown -R gitpod:gitpod /workspace/opensearch
sudo  chown -R gitpod:gitpod /workspace/logstash
ln -s /home/gitpod/logstash-7.13.2 /workspace/logstash/logstash-7.13.2
pyenv activate search_with_ml_week1
pip install -r /workspace/search_with_machine_learning_course/requirements_week1.txt
pyenv activate search_with_ml_week2
pip install -r /workspace/search_with_machine_learning_course/requirements_week2.txt
pyenv activate search_with_ml_week3
pip install -r /workspace/search_with_machine_learning_course/requirements_week3.txt
pyenv activate search_with_ml_week4
pip install -r /workspace/search_with_machine_learning_course/requirements_week4.txt


cd docker
docker-compose up -d

