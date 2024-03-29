# Surveys

## About The Project
This project started by me for education purposes. I started this project to improve my skills and learn more technologies. The most skill I wanted to improve was testing skill. And so I very tired to write a lot of tests for services, endpoints and utils stuff. I understand that it isn't at least 90% coverage, far from it and some tests are unnecessary, or I didn't write some necessary tests. I tried to stick to TDD approach and tried this approach on this project and received a lot of experience. And the second technology I wanted to explore more is async technology, and so I chose FastAPI as webframework and SQLAlchemy as ORM. I very like FasrtAPI because of its flexibility and opportunities (like dependency injection, pydantic compatibility and other wonderful out-of-the-box stuff) and so I chose FastAPI instead aiohttp's server api. And more I learn more about SQLAlchemy and used more of its asyncio core api and learned little more SQL then "select from".
I didn't take this project to complete (far away) and I leave in this project a lot of to do.

## Technologies
![python](https://img.shields.io/badge/Python3-yellow?style=for-the-badge&logo=python)
![fastapi](https://img.shields.io/badge/fastpi-white?style=for-the-badge&logo=fastapi)
![sqlalchemy](https://img.shields.io/badge/SQLAlchemy-red?style=for-the-badge)
![pytest](https://img.shields.io/badge/pytest-blue?style=for-the-badge&logo=pyetest)
![httpx](https://img.shields.io/badge/httpx-green?style=for-the-badge&logo=httpx)
![factory_boy](https://img.shields.io/badge/factory_boy-violet?style=for-the-badge)
![alembic](https://img.shields.io/badge/alembic-white?style=for-the-badge)
![fastapi](https://img.shields.io/badge/jinja_2-white?style=for-the-badge)

![docker](https://img.shields.io/badge/docker-blue?style=for-the-badge&logo=docker)
![docker_compose](https://img.shields.io/badge/docker_compose-blue?style=for-the-badge&logo=docker)

![git](https://img.shields.io/badge/git-white?style=for-the-badge&logo=git)

![postgres](https://img.shields.io/badge/postgresql-white?style=for-the-badge&logo=postgresql)

## How to run
1. Firstly you need to have installed docker and docker-compose to run the project.
2. You need to rename env.template to .env and fill in the following env vars

```
PROJECT_NAME
SECRET_KEY
SERVER_HOST
EMAIL_TEST_USER
SQL_ENGINE
SQL_USER
SQL_PASSWORD
SQL_DATABASE
SQL_HOST
SQL_PORT
DATABASE
PG_ADMIN_EMAIL
PG_ADMIN_PASSWORD
SMTP_TLS
SMTP_PORT
SMTP_HOST
SMTP_USER
SMTP_PASSWORD
EMAILS_FROM_EMAIL
ADMIN_FIXTURE_USERNAME
ADMIN_FIXTURE_EMAIL
ADMIN_FIXTURE_PASSWORD
ADMIN_FIXTURE_FIRST_NAME
ADMIN_FIXTURE_LAST_NAME
ADMIN_FIXTURE_BIRTH_DATE
```
3. And use this command`docker-compose up --build` and you're ready to use it.
4. There are two API web interfaces
- OpenAPI
    ![image fastapi](src/images/openapi.png)
- Redoc
    ![image redoc](src/images/redoc.png)


# Thanks for attention
