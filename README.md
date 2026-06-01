# HR Service

## Использовано

- **Python 3.12**
- **FastAPI**
- **SQLAlchemy 2.0**
- **PostgreSQL**
- **Alembic**
- **JWT**
- **Pytest**
- **Docker**

## Запуск через Docker

docker-compose up --build

## Остановка

docker-compose down

## Запуск тестов

docker-compose exec app python run_tests.py

## Логи

docker-compose logs -f

## API

Swagger: http://localhost:8000/docs
Health: http://localhost:8000/health