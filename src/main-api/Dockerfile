FROM golang:alpine as builder

WORKDIR /main-api

COPY ./src /main-api

RUN apk update && \
    apk upgrade && \
    go build -tags=jsoniter -o main-api .


FROM alpine

WORKDIR /main-api

COPY --from=builder /main-api/main-api /main-api

CMD [ "./main-api" ]