#!/bin/bash

start_dir=$(pwd)

for dir in ./*/; do
    cd $dir/
    if [ ! -f test.sh ]; then
        echo "No test.sh found in $dir... skipping"
        cd $start_dir
        continue
    fi
    chmod +x test.sh
    echo "Testing in $dir"
    ./test.sh
    if [ $? -ne 0 ]; then
        echo "Tests failed in $dir... exiting"
        exit 1
    fi
    cd $start_dir
done