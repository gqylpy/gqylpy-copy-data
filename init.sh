#!/usr/bin/env bash

docker build -t untitled/latest .

kubectl create -f yaml/
