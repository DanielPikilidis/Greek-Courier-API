#!/bin/bash

docker build --rm -t $1/proxy-manager .
docker push $1/proxy-manager:latest