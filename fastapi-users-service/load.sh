#!/bin/bash

for i in {1..10000}; do
  curl -s -o /dev/null -X 'GET' \
    'http://localhost:8000/api/v1/users/00' \
    -H 'accept: application/json'
done
