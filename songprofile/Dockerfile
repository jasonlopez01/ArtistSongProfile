#always start with FROM for base image/OS, docker site lists avail
FROM python:2.7-slim
MAINTAINER Jason Lopez <jasonlopez01@gmail.com>

#ENV sets var for path
ENV INSTALL_PATH /ArtistSongProfile
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip --no-cache-dir install -r requirements.txt

#copies current dir into docker image
COPY . .

#default cmd to run when docker img started
#gunicorn -b bind, all ip on localhost, log to std out (terminal not file), call create app
#__init__.py needed to use folder.py_module.py_function()
#build with docker-compose up --build, docker-compose up for running when already built; docker-compose stop
CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "app:create_app()"