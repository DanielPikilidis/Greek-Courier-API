#!/bin/bash

docker build --rm -t $1/skroutz-tracker .
docker push $1/skroutz-tracker:latest