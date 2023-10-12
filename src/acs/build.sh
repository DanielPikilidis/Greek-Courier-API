#!/bin/bash

docker build --rm -t $1/acs-tracker .
docker push $1/acs-tracker:latest