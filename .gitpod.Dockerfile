FROM gitpod/workspace-full:legacy-dazzle-v1

RUN sudo apt-get install -y graphviz
RUN pyenv install 3.9.7
# TODO: we are using 3.9.7 for the weekly projects, but here we are pip installing into the default for the Docker image.  We should probably create a pyenv.
RUN pip install kaggle
RUN pip install nltk
RUN pip install fasttext
RUN pip install xgboost
RUN pip install requests
RUN pip install ipython
RUN pip install urljoin
RUN pip install matplotlib
RUN pip install graphviz
RUN pip install pandas
RUN pip install numexpr
#RUN pip install bottleneck
RUN pip install flask

RUN pyenv virtualenv 3.9.7 search_with_ml_opensearch
RUN pyenv virtualenv 3.9.7 search_with_ml_week1
#RUN bash -c "export PATH="/home/gitpod/.pyenv/bin:$PATH" && eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate search_with_ml_week1 && pip install -r requirements_week1.txt"
RUN pyenv virtualenv 3.9.7 search_with_ml_week2
#RUN bash -c "export PATH="/home/gitpod/.pyenv/bin:$PATH" && eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate search_with_ml_week2 && pip install -r requirements_week2.txt"
RUN pyenv virtualenv 3.9.7 search_with_ml_week3
#RUN bash -c "export PATH="/home/gitpod/.pyenv/bin:$PATH" && eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate search_with_ml_week3 && pip install -r requirements_week3.txt"
RUN pyenv virtualenv 3.9.7 search_with_ml_week4
#RUN bash -c "export PATH="/home/gitpod/.pyenv/bin:$PATH" && eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate search_with_ml_week4 && pip install -r requirements_week4.txt"



RUN curl -o logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz https://artifacts.opensearch.org/logstash/logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN tar -xf logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN rm logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz

RUN wget https://github.com/facebookresearch/fastText/archive/v0.9.2.zip
RUN unzip v0.9.2.zip
RUN cd /home/gitpod/fastText-0.9.2 && /usr/bin/make -f /home/gitpod/fastText-0.9.2/Makefile fasttext
RUN rm v0.9.2.zip
