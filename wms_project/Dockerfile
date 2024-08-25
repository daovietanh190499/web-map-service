FROM python3.10

USER root

RUN apt update
RUN apt install -y gdal gdal-bin

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

USER wms
WORKDIR /home/wms
COPY . .