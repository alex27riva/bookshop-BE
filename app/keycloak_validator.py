import requests
import logging
import jwt

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

target_kid = 'mqp6ifE0E7ArXObW_1Cpshk8lwktc3Wklhk8UDlypPE'


class KeycloakValidator:
    def __init__(self, certs_url, client_id):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.certs_url = certs_url
        self.client_id = client_id
        self.public_key = self._get_public_key()

    def _get_public_key(self):
        response = requests.get(self.certs_url)
        keys = response.json()["keys"]
        print(keys)
        selected_key = next((key for key in keys if key['kid'] == target_kid), None)
        if selected_key:
            logging.debug(f"Selected key: {selected_key}")
            return selected_key
        return None

    def validate_token(self, token):
        try:
            decoded_token = jwt.decode(token, self.public_key, algorithms=['RS256'])
            print(decoded_token)
        except Exception as e:
            logging.error(f"Error decoding token: {e}")
