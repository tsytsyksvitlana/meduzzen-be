import bcrypt


class PasswordManager:
    """
    Class to hash and verify passwords.
    """

    DEFAULT_PASSWORD: str = "MyDefaul1tPa33w0rD/"

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify is plain password matches hashed password.
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @classmethod
    def return_default_password(cls) -> str:
        """
        Create a user with a default password.
        This method returns the hashed default password.
        """
        return cls.hash_password(cls.DEFAULT_PASSWORD)
