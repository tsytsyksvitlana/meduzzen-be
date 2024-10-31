import bcrypt


class PasswordManager:
    """
    Class to hash and verify passwords.
    """

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
