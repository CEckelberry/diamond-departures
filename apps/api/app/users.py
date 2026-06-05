# apps/api/app/users.py
from __future__ import annotations

from collections.abc import Callable

UserUpsert = Callable[[str, str, str | None, str | None], dict]


def in_memory_user_upsert(user_id: str, email: str, name: str | None, avatar_url: str | None) -> dict:
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}
