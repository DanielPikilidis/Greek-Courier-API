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

RUN adduser --disabled-password --gecos '' --uid 1001 appuser
USER 1001

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /elta-tracker
COPY /src/* /elta-tracker/

CMD [ "python3", "app.py" ]