#!/bin/bash

docker build --rm -t $1/geniki-tracker .
docker push $1/geniki-tracker:latest