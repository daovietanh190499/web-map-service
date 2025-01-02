FROM ubuntu:22.04

RUN apt update
RUN apt install -y gdal-bin libgdal-dev python3-gdal python3 python3-pip

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /home/wms
COPY . .