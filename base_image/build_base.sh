#!/usr/bin/env bash
cd "$(dirname "$0")"
cp ../requirements.txt ./
docker login local_docker_reg:8443
docker build -t local_docker_reg:8443/proxy_image .
rm -rf ./requirements.txt
docker push local_docker_reg:8443/proxy_image
