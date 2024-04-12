class TokenInfo:
    """
    This class simplifies access to information from a decoded JWT token.
    """

    def __init__(self, decoded_token):
        """Initializes the class with token

        Args:
         decoded_token (dict): The JWT token string.
        """

        self.decoded_token = decoded_token
        self.name = self.get('given_name')
        self.surname = self.get('family_name')
        self.email = self.get('email')

    def get(self, key) -> str:
        """Retrieves a specific value from the decoded token data.

        Args: key (str): The key of the desired value in the decoded token data. Valid keys: exp, iat, scope,
        email_verified, name, preferred_username, given_name, family_name, email

        Returns:
          The value associated with the given key, or None if the key is not found.
        """

        return self.decoded_token.get(key)

    def __str__(self):
        """
        Returns a string representation of the decoded token data.
        """
        return str(self.decoded_token)
