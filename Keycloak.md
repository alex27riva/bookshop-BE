# Keycloak

How to correctly configure Keycloak

## Client

Create a new client and give it a name (`client-id`).

### Access settings

**Root URL:** `http://localhost:8080/*`

**Home URL:** 'http://localhost:8080/*'

**Valid redirect URLs:** `*`  don't use this in production

**Valid post logout redirect URIs:** `+`

**Web origins:** `*`

**Admin URLs:** `http://localhost:8080/`


### Capability config

- enable _Client authentication_
