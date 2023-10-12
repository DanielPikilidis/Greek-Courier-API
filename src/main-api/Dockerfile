FROM golang:latest

RUN mkdir /main-api

WORKDIR /main-api

RUN apt update -y && apt upgrade -y

COPY /src/* /main-api/

RUN go build -tags=jsoniter .

CMD [ "./main-api" ]