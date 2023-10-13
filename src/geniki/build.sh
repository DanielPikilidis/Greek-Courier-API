#!/bin/bash

if [ "$2" ]; then
    tag="$2"
else
    tag="latest"
fi

docker build --rm -t $1/speedex-tracker --tag $1/speedex-tracker:$tag .
docker push $1/speedex-tracker:$tag