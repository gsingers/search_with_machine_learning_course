cd /workspace/datasets
# TODO: put in validation checks
pip install kaggle
echo "Downloading Kaggle"
kaggle competitions download -c acm-sf-chapter-hackathon-big
unzip acm-sf-chapter-hackathon-big.zip
tar -xf product_data.tar.gz