#!/usr/bin/env bash

original_dir=$(pwd)
parent_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)
cd "$parent_dir"

UUID=$(uuidgen)
sed "s/{ACCOUNT_ID}/${UUID}/g" account.yaml > account-${UUID}.yaml
minikube kubectl -- apply -f account-${UUID}.yaml
rm account-${UUID}.yaml

cd "$original_dir"
