#!/usr/bin/env bash

original_dir=$(pwd)
parent_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)
cd "$parent_dir"

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install postgresql -f values.yaml bitnami/postgresql

cd "$original_dir"
