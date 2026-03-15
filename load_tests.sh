#!/bin/bash

echo "Launching test environment..."
docker-compose -f docker-compose.load-test.yml up -d

pip install locust -q
echo "Launching load tests..."
locust -f tests/load/locustfile.py --host=http://localhost:8001 --users 50 --spawn-rate 5


echo "Clearing up test environment..."
docker-compose -f docker-compose.load-test.yml down -v
pip uninstall locust -q -y