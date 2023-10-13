#!/bin/bash

repo="dpikilidis"
tag="0.0.1"

start_dir=$(pwd)

for dir in ./*/; do
    cd $dir/
    chmod +x build.sh
    echo "Building in $dir"
    ./build.sh $repo $tag
    cd $start_dir
done