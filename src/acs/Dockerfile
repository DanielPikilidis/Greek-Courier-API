FROM python:3.12.1-slim-bullseye

RUN mkdir /acs-tracker

COPY /reqs/* /acs-tracker/

WORKDIR /acs-tracker

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install -r requirements.txt && \
    playwright install --with-deps chromium

COPY /src/* /acs-tracker/

CMD [ "python3", "app.py" ]