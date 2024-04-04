import requests
import logging
import jwt

from app.token_info import TokenInfo
from token_info import TokenInfo

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class KeycloakValidator:
    """
   This class validates tokens issued by a Keycloak server.

   It retrieves the public key from the Keycloak server and uses it to
   validate the token signature.

   Args:
       kc_url (KeycloakURLGenerator): Helper class to generate Keycloak URLs.
       client_id (str): The client ID of the application that issued the token.
       """

    def __init__(self, kc_url, client_id):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.realm_url = kc_url.realm_url()
        self.client_id = client_id
        self.public_key = self.get_public_key()

    def get_public_key(self) -> str:
        try:
            response = requests.get(self.realm_url)
            public_key = response.json()['public_key']
            public_key_pem = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
            self.public_key = public_key_pem
            return public_key_pem

        except requests.exceptions.RequestException as e:
            logging.error(f"Can't connect to {self.realm_url}")
            return ""

    def validate_token(self, token) -> TokenInfo | None:
        try:
            # Retry getting public key
            if self.public_key == "":
                self.get_public_key()

            # Decode token on if is valid
            decoded_token = jwt.decode(token, self.public_key, algorithms=['RS256'], audience='account')
            logging.debug(f"Decoded token {decoded_token}")
            return TokenInfo(decoded_token)
        except Exception as e:
            logging.error(f"Error decoding token: {e}")
            return None
