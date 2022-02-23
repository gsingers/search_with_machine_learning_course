FROM python:3.9.7

WORKDIR /usr/src/app

RUN pip install nltk==3.7
RUN pip install fasttext==0.9.2
RUN pip install xgboost==1.5.2
RUN pip install requests==2.26.0
RUN pip install ipython==7.27.0
RUN pip install urljoin==1.0.0
RUN pip install matplotlib==3.5.1
#RUN pip install graphviz
RUN pip install pandas==1.4.1
RUN pip install numexpr==2.8.1
#RUN pip install bottleneck
RUN pip install flask==2.0.2
ARG WEEK
COPY requirements_$WEEK.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_ENV=development
ENV FLASK_APP=$WEEK
RUN echo "week is: $WEEK"

EXPOSE 3000

CMD [ "flask", "run", "--port=3000", "--host=0.0.0.0"]