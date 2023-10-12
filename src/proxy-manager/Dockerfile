FROM golang:latest

RUN mkdir /proxy-manager

WORKDIR /proxy-manager

RUN apt update -y && apt upgrade -y

COPY /src/* /proxy-manager/

RUN go build .

CMD [ "./proxy-manager" ]