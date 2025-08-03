from jose import jwt
from jose.exceptions import JWTError
from fastapi import HTTPException, Request, Header
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
ALGORITHMS=["ES256"]

async def get_jwk():
    global jwks_cache
    if not jwks_cache:
        async with httpx.AsyncClient() as client:
            response = await client.get(os.getenv["SUPABASE_JWKS_URL"])
            if response.status_code != 200:
                raise Exception("Failed to fetch JWKS")
            jwks_cache = response.json()
    return jwks_cache

async def verify_jwt(token: str):
    jwks = await get_jwk()
    try:
        return jwt.decode(token, jwks, algorithms=ALGORITHMS, options={
            "verify_aud": False 
        })
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid JWT") from e

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ")[1]
    payload = await verify_jwt(token)
    return payload 
