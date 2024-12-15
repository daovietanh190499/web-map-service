FROM ghcr.io/andrii-rieznik/python-gdal:py3.12.6-gdal3.9.2

USER root

RUN apt update

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /home/wms
COPY . .