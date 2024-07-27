#!/usr/bin/env bash

original_dir=$(pwd)
parent_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)
cd "$parent_dir"

cd ../..

eval $(minikube docker-env)

docker build client -t dsp-client:latest
docker build manager -t dsp-manager:latest
docker build monitor -t dsp-monitor:latest

eval $(minikube docker-env -u)

cd "$original_dir"
