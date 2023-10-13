#!/bin/bash

if [ $2 -gt 0 ]; then
    tag="$2"
else
    tag="latest"
fi

docker build --rm -t $1/main-api --tag $1/main-api:$tag .
docker push $1/main-api:$tag