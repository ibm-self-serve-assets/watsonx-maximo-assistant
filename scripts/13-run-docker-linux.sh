#!/usr/bin/env bash

cd ..

podman run --env-file .env -d -p 8080:8080 --name maixmo-assist docker.io/gandigit/maixmo-assist

podman logs maixmo-assist