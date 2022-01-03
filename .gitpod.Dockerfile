FROM gitpod/workspace-full

RUN pyenv install 3.9.7
RUN pip install kaggle
RUN pyenv virtualenv 3.9.7 search_with_ml_opensearch


RUN sudo chown gitpod:gitpod /workspace
RUN mkdir -p /workspace/kaggle
RUN touch /workspace/kaggle/kaggle.json
RUN chmod 600 /workspace/kaggle/kaggle.json
RUN ln -s /workspace/kaggle /home/gitpod/.kaggle

RUN curl -o logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz https://artifacts.opensearch.org/logstash/logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN tar -xf logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
RUN rm logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz

RUN mkdir -p /workspace/opensearch
RUN mkdir -p /workspace/logstash
RUN mkdir -p /workspace/datasets
RUN sudo chown -R gitpod:gitpod /workspace/opensearch
RUN sudo  chown -R gitpod:gitpod /workspace/logstash


