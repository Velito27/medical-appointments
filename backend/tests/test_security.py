from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    password = "Example123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token("123")
    assert decode_access_token(token) == "123"
