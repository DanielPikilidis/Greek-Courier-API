#!/bin/bash

if [ "$2" ]; then
    tag="$2"
else
    tag="latest"
fi

docker build --rm --tag $1/geniki-tracker:$tag .
docker push $1/geniki-tracker:$tag