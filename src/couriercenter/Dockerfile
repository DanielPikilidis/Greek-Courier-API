FROM python:3.12.1-slim-bullseye

RUN mkdir /couriercenter-tracker

COPY /reqs/* /couriercenter-tracker/

WORKDIR /couriercenter-tracker

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install -r requirements.txt

COPY /src/* /couriercenter-tracker/

CMD [ "python3", "app.py" ]