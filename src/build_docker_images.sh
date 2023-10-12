#!/bin/bash

repo="dpikilidis"

start_dir=$(pwd)

for dir in ./*/; do
    cd $dir/
    chmod +x build.sh
    echo "Building in $dir"
    ./build.sh $repo
    cd $start_dir
done