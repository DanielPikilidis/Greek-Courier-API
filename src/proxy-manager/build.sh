#!/bin/bash

if [ $2 -gt 0 ]; then
    tag="$2"
else
    tag="latest"
fi

docker build --rm -t $1/proxy-manager --tag $1/proxy-manager:$tag .
docker push $1/proxy-manager:$tag