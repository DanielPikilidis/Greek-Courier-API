FROM python:3.11.4-slim-bullseye

RUN mkdir /acs-tracker

COPY /reqs/* /acs-tracker/

WORKDIR /acs-tracker

RUN apt update -y && apt upgrade -y

RUN pip3 install -r requirements.txt

RUN playwright install --with-deps chromium

COPY /src/* /acs-tracker/

CMD [ "python3", "app.py" ]