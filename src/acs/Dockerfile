FROM python:3.12.4-slim-bullseye as builder

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y && \
    pip3 install --upgrade pip

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY /reqs/* .
RUN pip3 install -r requirements.txt


FROM python:3.12.4-slim-bullseye

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers

RUN playwright install --with-deps chromium

RUN adduser --disabled-password --gecos '' --uid 1001 appuser
USER 1001

WORKDIR /acs-tracker
COPY /src/* /acs-tracker/

CMD [ "python3", "app.py" ]