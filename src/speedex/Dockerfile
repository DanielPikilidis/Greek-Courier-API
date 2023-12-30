FROM python:3.12.1-slim-bullseye

RUN mkdir /speedex-tracker

COPY /reqs/* /speedex-tracker/

WORKDIR /speedex-tracker

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install -r requirements.txt

COPY /src/* /speedex-tracker/

CMD [ "python3", "app.py" ]