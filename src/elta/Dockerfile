FROM python:3.11.4-slim-bullseye

RUN mkdir /elta-tracker

COPY /reqs/* /elta-tracker/

WORKDIR /elta-tracker

RUN apt update -y && apt upgrade -y

RUN pip3 install -r requirements.txt

COPY /src/* /elta-tracker/

CMD [ "python3", "app.py" ]