FROM golang:alpine as builder

WORKDIR /proxy-manager

COPY ./src /proxy-manager

RUN apk update && \
    apk upgrade && \
    go build -o proxy-manager .


FROM alpine

WORKDIR /proxy-manager

COPY --from=builder /proxy-manager/proxy-manager /proxy-manager

CMD [ "./proxy-manager" ]