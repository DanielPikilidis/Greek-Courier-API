#!/bin/bash

if [ "$2" ]; then
    tag="$2"
else
    tag="latest"
fi

docker build --rm -t $1/main-api:$tag .
docker push $1/main-api:$tag