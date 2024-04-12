class KeycloakURLGenerator:
    def __init__(self, base_url, realm_name, url_scheme="http"):
        """Generates URLs for interacting with a Keycloak server.

        Attributes:
            base_url (str): The base URL of the Keycloak server (without trailing slash).
            realm_name (str): The name of the Keycloak realm.
            url_scheme (str, optional): The URL scheme (default: "http").
        """
        self.base_url = base_url.rstrip("/")
        self.realm_name = realm_name
        self.url_scheme = url_scheme

    def _build_url(self, *args):
        """Constructs a URL based on the base URL, realm name, and provided arguments.

        Args:
            *args (str): Additional path segments to append to the URL.

        Returns:
            str: The complete URL string.
        """
        return "/".join([self.url_scheme + '://' + self.base_url, "realms", self.realm_name] + list(args))

    def introspect_url(self):
        """Generates the URL for the Keycloak token introspection endpoint.

        Returns:
            str: The URL for token introspection.
        """
        return self._build_url("protocol", "openid-connect", "token", "introspect")

    def userinfo_url(self):
        """Generates the URL for the Keycloak userinfo endpoint.

        Returns:
            str: The URL for userinfo endpoint.
        """
        return self._build_url("protocol", "openid-connect", "userinfo")

    def certs_url(self):
        """Generates the URL for the Keycloak certs endpoint.

        Returns:
            str: The URL for certs endpoint.
        """
        return self._build_url("protocol", "openid-connect", "certs")

    def realm_url(self):
        """Generates the base URL for the Keycloak realm.

        Returns:
            str: The base URL for the realm.
        """
        return self._build_url()

    def logout_url(self):
        """Generates the URL for the Keycloak logout endpoint.

        Returns:
            str: The URL for logout endpoint.
        """
        return self._build_url("protocol", "openid-connect", "logout")
