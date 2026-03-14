#!/bin/bash

echo "Запускаем тестовое окружение..."
docker-compose -f docker-compose.load-test.yml up -d


echo "Запускаем нагрузочное тестирование..."
locust -f tests/load/locustfile.py --host=http://localhost:8001 --users 50 --spawn-rate 5


echo "Очищаем тестовое окружение..."
docker-compose -f docker-compose.load-test.yml down -v