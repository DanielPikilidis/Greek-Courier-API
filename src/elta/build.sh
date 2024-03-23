#!/bin/bash

if [ "$2" ]; then
    tag="$2"
else
    tag="latest"
fi

docker build --rm --tag $1/elta-tracker:$tag .
docker push $1/elta-tracker:$tag