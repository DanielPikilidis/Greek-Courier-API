FROM golang:latest

RUN mkdir /skroutz-tracker

WORKDIR /skroutz-tracker

RUN apt update -y && \
    apt upgrade -y && \
    apt autoremove -y

COPY /src/* /skroutz-tracker/

RUN go build -o skroutz-tracker

CMD [ "./skroutz-tracker" ]