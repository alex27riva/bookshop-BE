# bookshop-BE

Bookshop backend written in Python / Flask

## Run
Use [Pycharm](https://www.jetbrains.com/pycharm/) for development or follow the following instruction for manual install.

### Manual install

- Clone the repo and `cd` into it
- create a `.env` in the root of the project with the example below
- create Python venv `python3 -m venv venv`
- Enter venv `source venv/bin/activate`
- Install dependencies `pip3 install -r requirements.txt`
- Finally, run the app `python3 app/app.py`

## Keycloak configuration
See [Keycloak.md](Keycloak.md) for details.

## Flask Configuration

Create a .env file in the root of the project with the following values

```
CLIENT_ID=bookshop
KEYCLOAK_URI_SCHEME=http
KEYCLOAK_HOST=localhost:8080
KEYCLOAK_REALM=unimi
SECRET_KEY=
```

Generate a secure `SECRET_KEY` with:

```bash
openssl rand -base64 32
```

## API documentation

See table in [API.md](API.md).
