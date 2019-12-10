#!/usr/bin/env bash
cd "$(dirname "$0")"
docker login local_docker_reg:8443
docker build -t local_docker_reg:8443/proxy_image .
docker push local_docker_reg:8443/proxy_image