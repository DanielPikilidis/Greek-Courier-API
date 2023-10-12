#!/bin/bash

docker build --rm -t $1/easymail-tracker .
docker push $1/easymail-tracker:latest