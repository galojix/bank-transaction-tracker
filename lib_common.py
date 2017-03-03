from passlib.hash import pbkdf2_sha256
import dateutil.parser

def hash_password(password):
    # generate new salt, and hash a password    
    return pbkdf2_sha256.hash(password)

    
def password_verified(password, hash):
    return pbkdf2_sha256.verify(password, hash)
    
   
