import requests
import logging
import jwt
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
        """Retrieves the public key from the configured realm URL.

        Attempts to fetch the public key from the provided realm URL. If successful,
        formats the key as PEM and caches it internally. Otherwise, logs an error
        and returns an empty string.

        Returns:
            str: The public key in PEM format on success, otherwise an empty string.
        """
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
        """Attempts to validate a JSON Web Token (JWT).

        First, retrieves the public key if not already cached. Then, it tries to
        decode the provided JWT using the RS256 algorithm and a specific audience.
        On successful decoding, a TokenInfo object is returned with the decoded data.
        Otherwise, logs the error and returns None.

        Args:
            token (str): The JWT token to be validated.

        Returns:
            TokenInfo | None: A TokenInfo object containing decoded token information
                on success, None otherwise.
        """
        try:
            # Retry getting public key
            if self.public_key == "":
                self.get_public_key()

            # Decode token on if is valid
            decoded_token = jwt.decode(token, self.public_key, algorithms=['RS256'], audience='account')
            logging.debug(f"Decoded token {decoded_token}")
            return TokenInfo(decoded_token)

        except jwt.exceptions.DecodeError as e:
            logging.error(f"Error decoding token: Invalid format or signature - {e}")
            return None

        except jwt.exceptions.ExpiredSignatureError as e:
            logging.error(f"Error decoding token: Token expired - {e}")
            return None

        except AttributeError as e:
            logging.debug(f"Error accessing an attribute - {e}")

        except Exception as e:
            logging.error(f"Unexpected error decoding token: - {e}")
            return None
