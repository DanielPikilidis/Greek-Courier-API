#!/bin/bash

docker build --rm -t $1/main-api .
docker push $1/main-api:latest