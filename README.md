# bookshop-BE

Bookshop backend using Flask

## Keycloak configuration
See [Keycloak.md](Keycloak.md) for details.

## Flask Configuration
Create a .env file in the root of the project with the following values

```
CLIENT_ID=flask-demo
CLIENT_SECRET=
REDIRECT_URI=http://localhost:8000/welcome
KEYCLOAK_TOKEN_ENDPOINT=http://localhost:8080/realms/{your_realm}/protocol/openid-connect/token
```

