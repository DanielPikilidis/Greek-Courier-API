FROM golang:alpine as builder

WORKDIR /main-api

COPY ./src /main-api

RUN apk update && \
    apk upgrade && \
    go build -tags=jsoniter -o main-api .


FROM alpine

RUN adduser --disabled-password --gecos '' --uid 1001 appuser
USER 1001

WORKDIR /main-api

COPY --from=builder /main-api/main-api /main-api

CMD [ "./main-api" ]