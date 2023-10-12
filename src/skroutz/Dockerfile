FROM golang:latest

RUN mkdir /skroutz-tracker

WORKDIR /skroutz-tracker

RUN apt update -y && apt upgrade -y

COPY /src/* /skroutz-tracker/

RUN go build -o skroutz-tracker

CMD [ "./skroutz-tracker" ]