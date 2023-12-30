FROM python:3.12.1-slim-bullseye

RUN mkdir /geniki-tracker

COPY /reqs/* /geniki-tracker/

WORKDIR /geniki-tracker

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install -r requirements.txt

COPY /src/* /geniki-tracker/

CMD [ "python3", "app.py" ]