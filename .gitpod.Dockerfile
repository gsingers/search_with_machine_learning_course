FROM gitpod/workspace-full

RUN sudo apt-get install -y graphviz
RUN pyenv install 3.9.7
RUN pip install kaggle
RUN pip install nltk
RUN pip install fasttext
RUN pip install xgboost
RUN pip install requests
RUN pip install ipython
RUN pip install urljoin
RUN pip install matplotlib
RUN pip install graphviz
RUN pip install bottleneck

RUN pyenv virtualenv 3.9.7 search_with_ml_opensearch
RUN pyenv virtualenv 3.9.7 search_with_ml_week1
RUN pyenv virtualenv 3.9.7 search_with_ml_week2
RUN pyenv virtualenv 3.9.7 search_with_ml_week3
RUN pyenv virtualenv 3.9.7 search_with_ml_week4



RUN curl -o logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz https://artifacts.opensearch.org/logstash/logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN tar -xf logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN rm logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz

RUN wget https://github.com/facebookresearch/fastText/archive/v0.9.2.zip
RUN unzip v0.9.2.zip
RUN cd /home/gitpod/fastText-0.9.2 && /usr/bin/make -f /home/gitpod/fastText-0.9.2/Makefile fasttext
