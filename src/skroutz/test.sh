#!/bin/bash

cd src/

go clean -testcache

go test -v ./...

if [ $? -ne 0 ]; then
    echo "Failed test ... exiting"
    exit 1
fi 