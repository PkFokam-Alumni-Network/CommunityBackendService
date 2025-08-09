# CommunityBackendService

The part of the community website hosting all the backend and the services

# PRE-REQUISITES

- Python version 3.12
- Docker desktop
- Postman

# HOW TO GET STARTED

- Clone the repo with: `git clone https://github.com/PkFokam-Alumni-Network/CommunityBackendService.git`
- Create a virtual environment to hold your dependencies:
  - Windows: `py -3 -m venv venv`
  - MacOS: `python3 -m venv venv`
- Activate your virtual environment
  - Windows: `venv\Scripts\activate.bat`
  - MacOS: `source venv/bin/activate`
- Install the latest dependencies
  - pip install -r requirements.txt
- Setup your .env file (reach out in paci-website discord channel for a sample) or copy from [here](https://github.com/orgs/PkFokam-Alumni-Network/discussions/3)

# HOW TO RUN YOUR SERVER LOCALLY

- `docker compose -f docker-compose.dev.yaml build`
- `docker compose -f docker-compose.dev.yaml up`

# HOW TO MAKE CODE CHANGES

- Create a new branch from main with the format yourName/what-you-are-trying-to-do
  - For example, `warren/create-user-object`
- Make your code changes
- Push and submit and PR
  [Example PR](https://github.com/PkFokam-Alumni-Network/CommunityBackendService/pull/9)

# TESTING

## Unit Tests

We use Pytest as our unit testing framework. Here are some commands to run tests (we assume you are in the root folder of the project):

- run all tests: `pytest`
- run all tests of a particular file (e.g: announcement_test.py): `pytest .\tests\announcement_test.py`
- run a specific test from a file(e.g test_get_non_existing_announcement): `pytest .\tests\announcement_test.py::test_get_non_existing_announcement`

## Integration Tests

- If you make changes to anything involving the API (a request input, a response, new headers, new auth), you should have a test with Postman to evaluate if your change works as expected at the HTTP level. Use Postman to make the relevant API calls and see if you get the expected response.

# HELPFUL RESOURCES

- [FastAPI Documentation](https://fastapi.tiangolo.com/)

# CODE GUIDES

- Always use static typing when possible.
- Always use named parameters instead of positional parameters when a function takes more than 1 argument
- If a function has two many arguments, use dataclasses
- Always make the migration and model PRs separate from your feature changes

# ALEMBIC MIGRATIONS

1. Run your server locally

- `docker compose -f docker-compose.dev.yaml up`
- `docker compose -f docker-compose.dev.yaml build`

2. Make a change to the models
3. Change this line `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)` to `config.set_main_option("sqlalchemy.url", "postgresql://user:password@localhost:5432/test_db")`
4. Generate the migration file with `alembic revision --autogenerate -m "Purpose of the migration"`
5. Apply the migration with `alembic upgrade head`
6. Revert 3.

# DESIGN AND DATA MODEL

- [Docs](https://docs.google.com/document/d/1tOZmcg-oa32PrtxE-sImnDYidz3Gw6cjE0YvSzqt7Bo/edit?usp=sharing)
