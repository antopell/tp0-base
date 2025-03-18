#!/bin/bash

# docker setup
./generar-compose.sh docker-compose-dev.yaml 1
make docker-image
# con d para liberar la terminal
docker compose -f docker-compose-dev.yaml up server -d

PORT="$(grep "SERVER_PORT = " ./server/config.ini  | cut -d ' ' -f3)"
IP="$(grep "SERVER_IP = " ./server/config.ini  | cut -d ' ' -f3)"

echo "${PORT}"
echo "${IP}"

docker compose -f docker-compose-dev.yaml down

