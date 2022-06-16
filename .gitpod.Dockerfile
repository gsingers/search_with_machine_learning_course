FROM gitpod/workspace-full:latest
#docker pull gitpod/workspace-full:2022-06-09-20-58-43
RUN sudo apt-get install -y graphviz

# Move where Pyenv is stored
#RUN sudo mv /home/gitpod/.pyenv /workspace/pyenv
#RUN sudo ln -s /workspace/pyenv /home/gitpod/.pyenv

RUN wget -O /home/gitpod/requirements.txt https://raw.githubusercontent.com/gsingers/search_with_machine_learning_course/main/requirements.txt

RUN echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> /home/gitpod/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> /home/gitpod/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> /home/gitpod/.bashrc

RUN pyenv install 3.9.7
RUN pyenv global 3.9.7
RUN pip install kaggle

RUN pyenv virtualenv 3.9.7 search_with_ml
RUN bash  -i -c "pyenv activate search_with_ml && pip install -r /home/gitpod/requirements.txt"



RUN wget https://github.com/facebookresearch/fastText/archive/v0.9.2.zip
RUN unzip v0.9.2.zip
RUN cd /home/gitpod/fastText-0.9.2 && /usr/bin/make -f /home/gitpod/fastText-0.9.2/Makefile fasttext

#RUN rm v0.9.2.zip