# Set the base image to use Alpine
FROM python:3.6.1

MAINTAINER Gustav Olsson

ENV PYTHONBUFFERED 1
ENV DJANGO_SETTINGS_MODULE supervisord_overseer.settings.docker
RUN mkdir /config /src
ADD ./config/ /config/
RUN pip install -r /config/requirements.txt

WORKDIR /src
