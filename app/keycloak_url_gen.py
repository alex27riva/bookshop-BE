class KeycloakURLGenerator:
    def __init__(self, base_url, realm_name, url_scheme="http"):
        self.base_url = base_url.rstrip("/")
        self.realm_name = realm_name
        self.url_scheme = url_scheme

    def _build_url(self, *args):
        return "/".join([self.url_scheme + '://' + self.base_url, "realms", self.realm_name] + list(args))

    def introspect_url(self):
        return self._build_url("protocol", "openid-connect", "token", "introspect")

    def userinfo_url(self):
        return self._build_url("protocol", "openid-connect", "userinfo")

    def certs_url(self):
        return self._build_url("protocol", "openid-connect", "certs")

    def logout_url(self):
        return self._build_url("protocol", "openid-connect", "logout")
