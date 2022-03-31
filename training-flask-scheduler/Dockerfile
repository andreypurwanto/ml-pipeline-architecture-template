FROM python:3.7
RUN apt-get update -y
RUN apt-get install -y python3 python3-dev python3-pip nginx
ENV CONTAINER_HOME=/var/www
ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME
RUN pip3 install -r $CONTAINER_HOME/requirements.txt
CMD ["gunicorn", "--bind",  ":5555", "app.main:app"]
