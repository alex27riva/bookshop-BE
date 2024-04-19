import os

from dotenv import load_dotenv


class Environment:
    """A class to manage environment variables.

  Attributes:
      CLIENT_ID: The value of the 'CLIENT_ID' environment variable.
      KEYCLOAK_URI_SCHEME: The value of the 'KEYCLOAK_URI_SCHEME' environment variable.
      KEYCLOAK_HOST: The value of the 'KEYCLOAK_HOST' environment variable.
      REALM: The value of the 'KEYCLOAK_REALM' environment variable.
    """

    def __init__(self):
        """Reads environment variables and sets them as class attributes.

        Raises:
            KeyError: If a required environment variable is not found.
        """
        load_dotenv()
        self.CLIENT_ID = os.getenv('CLIENT_ID')
        self.KEYCLOAK_URI_SCHEME = os.getenv('KEYCLOAK_URI_SCHEME')
        self.KEYCLOAK_HOST = os.getenv('KEYCLOAK_HOST')
        self.REALM = os.getenv('KEYCLOAK_REALM')
        self.SECRET_KEY = os.getenv('SECRET_KEY')

        # Check for required variables
        required_vars = ['CLIENT_ID', 'KEYCLOAK_URI_SCHEME', 'KEYCLOAK_HOST', 'REALM']
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        if missing_vars:
            raise KeyError(f"Missing required environment variables: {', '.join(missing_vars)}")
