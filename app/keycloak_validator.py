import requests
import logging
import jwt

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class KeycloakValidator:
    def __init__(self, certs_url, client_id):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.certs_url = certs_url
        self.client_id = client_id
        self.public_key = self._get_public_key()

    def _get_public_key(self):
        response = requests.get(self.certs_url)
        keys = response.json()["keys"]
        for key in keys:
            if key["kid"]:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        return None

