#!/bin/bash

# docker setup
sh ./generar-compose.sh docker-compose-dev.yaml 1
make docker-compose-up

PORT=$(grep "SERVER_PORT = " ./server/config.ini  | cut -d ' ' -f3)
IP=$(grep "SERVER_IP = " ./server/config.ini  | cut -d ' ' -f3)

TESTING_STR='testing'

RES=$(docker exec client1 sh -c "echo $TESTING_STR | nc $IP $PORT")

if [ $RES == $TESTING_STR ]
then
  echo "action: test_echo_server | result: success"
else
  echo "action: test_echo_server | result: fail"
fi

make docker-compose-down

