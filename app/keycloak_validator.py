import requests
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class KeycloakValidator:
    def __init__(self, introspect_url, client_id):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.introspect_url = introspect_url
        self.client_id = client_id

    def validate_token(self, token):
        data = {
            'token': token,
            'client_id': self.client_id
        }

        response = requests.post(self.introspect_url, data=data)
        self.logger.debug(response.json())

        if response.status_code == 200:
            self.logger.debug("Token sent to Keycloak")
            response_data = response.json()
            return response_data.get('active', False)
        else:
            return False
