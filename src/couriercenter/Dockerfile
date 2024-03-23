FROM python:3.12.2-alpine3.19 as builder

RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3-dev build-base && \
    pip3 install --upgrade pip

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY /reqs/* .
RUN pip3 install -r requirements.txt


FROM python:3.12.2-alpine3.19

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /couriercenter-tracker
COPY /src/* /couriercenter-tracker/

CMD [ "python3", "app.py" ]