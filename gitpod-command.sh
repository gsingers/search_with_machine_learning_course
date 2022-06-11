ln -s /workspace/kaggle /home/gitpod/.kaggle

mkdir -p /workspace/opensearch
mkdir -p /workspace/datasets
sudo chown -R gitpod:gitpod /workspace/opensearch


mkdir /workspace/ltr_output
cp data/validity.csv /workspace/ltr_output/

cd docker
docker-compose up -d

