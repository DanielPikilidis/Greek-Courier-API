#!/bin/bash

docker build --rm -t dpikilidis/couriercenter-tracker .
docker push $1/couriercenter-tracker:latest