FROM golang:latest

RUN mkdir /main-api

WORKDIR /main-api

RUN apt update -y && apt upgrade -y

COPY /src/*.go /main-api/
COPY /src/go.mod /main-api/
COPY /src/go.sum /main-api/
COPY /src/docs/ /main-api/docs/

RUN go build -tags=jsoniter .

CMD [ "./main-api" ]