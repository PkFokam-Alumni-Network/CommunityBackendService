# CommunityBackendService

The part of the community website hosting all the backend and the services

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

# HOW TO RUN YOUR SERVER LOCALLY

- `uvicorn main:app --reload`

# HOW TO MAKE CODE CHANGES

- Create a new branch from main with the format yourName/what-you-are-trying-to-do
  - For example, `warren/create-user-object`
- Make your code changes
- Push and submit and PR
  [Example PR](https://github.com/PkFokam-Alumni-Network/CommunityBackendService/pull/9)

# TESTING

- [Postman Collections](https://solar-shadow-655969.postman.co/workspace/Team-Workspace~b5dc0fe3-7281-4a8b-8693-293940ef7aff/collection/29422822-1d267a27-51a3-4860-893e-ed410410f187?action=share&creator=29422822)

# HELPFUL RESOURCES

- [FastAPI Documentation](https://fastapi.tiangolo.com/)

# CODE GUIDES

- Always use static typing when possible.
- Always use named parameters instead of positional parameters when a function takes more than 1 argument

# ALEMBIC MIGRATIONS

- Make a copy of the database from S3 bucket
- Make a change to the models
- alembic revision -m "{Purpose of the migration}"
- Log in to the docker container and run `alembic upgrade head`

# DESIGN AND DATA MODEL

- [Docs](https://docs.google.com/document/d/1tOZmcg-oa32PrtxE-sImnDYidz3Gw6cjE0YvSzqt7Bo/edit?usp=sharing)
