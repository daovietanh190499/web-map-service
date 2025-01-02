FROM python:3.7-bullseye

USER root

RUN apt update
RUN apt install -y software-properties-common
# RUN add-apt-repository ppa:ubuntugis/ppa
# RUN apt update
RUN apt install -y gdal-bin libgdal-dev

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal


COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /home/wms
COPY . .