FROM python:3.11.4-slim-bullseye

RUN mkdir /geniki-tracker

COPY /reqs/* /geniki-tracker/

WORKDIR /geniki-tracker

RUN apt update -y && apt upgrade -y

RUN pip3 install -r requirements.txt

COPY /src/* /geniki-tracker/

CMD [ "python3", "app.py" ]