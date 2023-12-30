FROM python:3.12.1-slim-bullseye

RUN mkdir /elta-tracker

COPY /reqs/* /elta-tracker/

WORKDIR /elta-tracker

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install -r requirements.txt

COPY /src/* /elta-tracker/

CMD [ "python3", "app.py" ]