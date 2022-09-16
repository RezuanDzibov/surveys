import jwt
from httpx import AsyncClient

from app.core import jwt as auth_jwt
from app.core.settings import get_settings
from app.models import User

settings = get_settings()


async def test_create_token(admin_user: User, test_client: AsyncClient):
    token = auth_jwt.create_access_token(user_id=admin_user.id)
    response = await test_client.get(
        "user/me",
        headers={
            "Authorization": f"Bearer {token.get('access_token')}"
        }
    )
    assert response.status_code == 200


async def test_create_jwt_token(admin_user: User):
    token = auth_jwt.create_access_token(user_id=admin_user.id).get("access_token")
    decoded_access_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
    assert decoded_access_token.get("user_id") == str(admin_user.id)
