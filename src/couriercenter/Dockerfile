FROM python:3.11.4-slim-bullseye

RUN mkdir /couriercenter-tracker

COPY /reqs/* /couriercenter-tracker/

WORKDIR /couriercenter-tracker

RUN apt update -y && apt upgrade -y

RUN pip3 install -r requirements.txt

COPY /src/* /couriercenter-tracker/

CMD [ "python3", "app.py" ]