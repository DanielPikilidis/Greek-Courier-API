FROM golang:alpine as builder

WORKDIR /skroutz-tracker

COPY ./src /skroutz-tracker

RUN apk update && \
    apk upgrade && \
    go build -tags=jsoniter -o skroutz-tracker .


FROM alpine

RUN apk add --no-cache tzdata

WORKDIR /skroutz-tracker

COPY --from=builder /skroutz-tracker/skroutz-tracker /skroutz-tracker

CMD [ "./skroutz-tracker" ]