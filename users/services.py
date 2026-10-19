
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


def google_login(code):
    # 1. Проверяем настройки OAuth
    if not all([
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        settings.GOOGLE_REDIRECT_URI,
    ]):
        raise ValueError("Google OAuth не настроен в .env")

    # 2. Обмениваем authorization code на токен Google
    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    token_response.raise_for_status()
    google_tokens = token_response.json()

    google_access_token = google_tokens.get("access_token")
    if not google_access_token:
        raise ValueError("Google не вернул access_token")

    # 3. Получаем профиль пользователя
    profile_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={
            "Authorization": f"Bearer {google_access_token}",
        },
        timeout=10,
    )
    profile_response.raise_for_status()
    profile = profile_response.json()

    email = profile.get("email")
    if not email:
        raise ValueError("Google не вернул email пользователя")

    # 4. Ищем пользователя или создаём нового
    user = User.objects.filter(email__iexact=email).first()
    is_new_user = user is None

    if is_new_user:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=None,
            role="student",
        )

    # 5. Создаём JWT-токены нашего Django API
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "is_new_user": is_new_user,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
    }
