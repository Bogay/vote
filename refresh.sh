#!/bin/bash

while :
do
    echo "refresh..."
    curl --request POST http://localhost:8000/topic/refresh
    sleep 5s
done
