#!/bin/bash

docker build --rm -t $1/elta-tracker .
docker push $1/elta-tracker:latest