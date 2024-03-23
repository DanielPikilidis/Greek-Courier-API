FROM python:3.12.2-slim-bullseye as builder

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install --upgrade pip

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY /reqs/* .
RUN pip3 install -r requirements.txt


FROM python:3.12.2-slim-bullseye

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN playwright install --with-deps chromium

WORKDIR /acs-tracker
COPY /src/* /acs-tracker/

CMD [ "python3", "app.py" ]