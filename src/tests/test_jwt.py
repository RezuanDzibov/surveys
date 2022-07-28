import jwt

from app.core import jwt as auth_jwt
from app.core.settings import get_settings

settings = get_settings()


def test_create_token(admin_user, test_client):
    token = auth_jwt.create_acess_token(user_id=str(admin_user.id))
    response = test_client.get(
        "users/me",
        headers={
            "Authorization": f"Bearer {token.get('access_token')}"
        }
    )
    assert response.status_code == 200


def test_create_jwt_token(admin_user):
    token = auth_jwt.create_acess_token(user_id=str(admin_user.id)).get("access_token")
    decoded_access_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
    assert decoded_access_token.get("user_id") == str(admin_user.id)
