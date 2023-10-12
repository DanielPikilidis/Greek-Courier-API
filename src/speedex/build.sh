#!/bin/bash

docker build --rm -t $1/speedex-tracker .
docker push $1/speedex-tracker:latest