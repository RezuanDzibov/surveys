from app.core import security


def test_password_hashing():
    hashed_password = security.get_password_hash(password="password")
    assert security.verify_password(plain_password="password", hashed_password=hashed_password)