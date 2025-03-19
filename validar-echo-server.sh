#!/bin/bash

PORT=$(grep "SERVER_PORT = " ./server/config.ini  | cut -d ' ' -f3)
IP=$(grep "SERVER_IP = " ./server/config.ini  | cut -d ' ' -f3)

TESTING_STR='testing'

RES=$(docker run --net tp0_testing_net busybox:latest sh -c "echo $TESTING_STR | nc $IP $PORT")

if [ "$RES" = "$TESTING_STR" ]
then
  echo "action: test_echo_server | result: success"
else
  echo "action: test_echo_server | result: fail"
fi
