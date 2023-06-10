#!/bin/bash

sudo docker run --rm --pull always -p 8080:8000 surrealdb/surrealdb:latest start \
    --user root \
    --pass root \
    memory