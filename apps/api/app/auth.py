# apps/api/app/auth.py
from __future__ import annotations

from fastapi import Header, HTTPException
from jose import JWTError, jwt


def make_jwt_verifier(secret: str):
    def verify(authorization: str | None = Header(default=None)) -> dict:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        token = authorization.removeprefix("Bearer ")
        try:
            return jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return verify
