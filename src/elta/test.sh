#!/bin/bash

pip3 install -r reqs/requirements.txt

# unittest discover is complete garbage, like I can't even specify a directory... so I have to do this
for file in $(find . -name "*_test.py"); do
    echo "Running test: $file"
    python3 $file
    if [ $? -ne 0 ]; then
        echo "Failed test: $file... exiting"
        exit 1
    fi
done

rm -rf src/__pycache__/ 