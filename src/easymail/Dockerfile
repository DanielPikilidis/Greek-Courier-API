FROM python:3.12.1-slim-bullseye

RUN mkdir /easymail-tracker

COPY /reqs/* /easymail-tracker/

WORKDIR /easymail-tracker

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install -r requirements.txt

COPY /src/* /easymail-tracker/

CMD [ "python3", "app.py" ]