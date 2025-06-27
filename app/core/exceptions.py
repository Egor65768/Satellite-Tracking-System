class AccessDeniedError(Exception):
    """Ошибка доступа (не хватает прав)."""

    def __init__(self, detail: str = "Access denied"):
        self.detail = detail


class AdminPasswordRequiredError(AccessDeniedError):
    """Требуется пароль администратора."""

    def __init__(self):
        super().__init__("Admin access denied. Invalid or missing admin password.")


class UserPasswordRequiredError(AccessDeniedError):
    """Требуется пароль пользователя."""

    def __init__(self):
        super().__init__("Invalid or missing user password.")


class EmailNotFoundError(Exception):
    """Email не найден в базе данных."""

    def __init__(self, email: str = None):
        detail = "Email not found in database"
        if email:
            detail = f"Email '{email}' not found in database"
        super().__init__(detail)


class InvalidPasswordError(Exception):
    """Неверный пароль (не совпадает с паролем в базе)."""

    def __init__(self):
        super().__init__("Invalid password")


class NewPasswordMatchesOldError(Exception):
    """Новый пароль совпадает со старым."""

    def __init__(self):
        super().__init__("New password must be different from the old one")


class InvalidRefreshToken(Exception):
    """Невалидный refresh-токен"""

    def __init__(self):
        super().__init__("Refresh token is invalid")


class InvalidAccessToken(Exception):
    """Невалидный access-токен"""

    def __init__(self):
        super().__init__("Access token is invalid")


class AccessTokenExpiredError(Exception):
    """Срок действия access-токен закончился"""

    def __init__(self):
        super().__init__("Access token expired")


class RefreshTokenExpiredError(Exception):
    """Срок действия refresh-токен закончился"""

    def __init__(self):
        super().__init__("Refresh token expired")


class RefreshTokenNotFoundError(Exception):
    """Вызывается, когда токен валиден, но не найден в БД."""

    def __init__(self):
        super().__init__("Refresh token not found in db")


class UserNotFoundError(Exception):
    """Вызывается, когда пользователь по данному id не найден в БД."""

    def __init__(self):
        super().__init__("User by this id not found in db")
