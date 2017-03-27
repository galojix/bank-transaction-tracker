"""Module that contains password functions."""
from passlib.hash import pbkdf2_sha256


def hash_password(password):
    """Generate new salt, hash password and return both."""
    return pbkdf2_sha256.hash(password)


def password_verified(password, hash):
    """Verify password and return status."""
    return pbkdf2_sha256.verify(password, hash)
