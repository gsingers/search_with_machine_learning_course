FROM gitpod/workspace-full

RUN pyenv install 3.9.7
RUN pip install kaggle
RUN pip install nltk
RUN pip install fasttext

RUN pyenv virtualenv 3.9.7 search_with_ml_opensearch

RUN curl -o logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz https://artifacts.opensearch.org/logstash/logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN tar -xf logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN rm logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz

RUN wget https://github.com/facebookresearch/fastText/archive/v0.9.2.zip
RUN unzip v0.9.2.zip
RUN rm v0.9.2.zip
RUN (cd fastText-0.9.2 && make)

RUN wget https://dl.fbaipublicfiles.com/fasttext/data/cooking.stackexchange.tar.gz
RUN tar xvzf cooking.stackexchange.tar.gz
RUN rm cooking.stackexchange.tar.gz
