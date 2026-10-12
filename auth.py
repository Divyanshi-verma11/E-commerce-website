from pwdlib import PasswordHash
from jose import jwt


# Create password hashing object
password_hash = PasswordHash.recommended()


# Secret key for JWT
SECRET_KEY = "my-secret-key"

# Algorithm used for JWT
ALGORITHM = "HS256"


# =========================
# PASSWORD HASHING
# =========================

def hash_password(password):

    return password_hash.hash(password)


# =========================
# PASSWORD VERIFICATION
# =========================

def verify_password(password, hashed_password):

    return password_hash.verify(
        password,
        hashed_password
    )


# =========================
# CREATE JWT TOKEN
# =========================

def create_token(user_id, role):

    data = {
        "user_id": user_id,
        "role": role
    }

    token = jwt.encode(
        data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token