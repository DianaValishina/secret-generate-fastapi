from fastapi import APIRouter, HTTPException
from typing import Annotated
from src.schemas import SecretCodeAdd, SecretKey, SecretGenerate
from fastapi import Depends
from cryptography.fernet import Fernet
from src.db.secrets import SecretsDAL
from src.db.auto_delete import AutoDeleteDAL
import asyncpg
from config.config import DATABASE_URL


router = APIRouter(
    tags=["Секретный код"])


@router.post("/generate")
async def generate_secret_key(
    secret: Annotated[SecretCodeAdd, Depends()]
) -> SecretKey:
    secret_dict = secret.model_dump()

    # the secret key
    cipher_key = Fernet.generate_key()

    # encrypting data received from the user
    secret_encrypted = await encrypt(cipher_key, secret_dict["secret_text"])
    passphrase_encrypted = await encrypt(cipher_key, secret_dict["passphrase"])

    async with asyncpg.create_pool(DATABASE_URL) as conn:
        await SecretsDAL(conn).delete_expired_secrets()

        auto_delete_id = (await AutoDeleteDAL(conn).
                          get_id(secret_dict["auto_delete"]))

        await SecretsDAL(conn).insert_secret(
                                cipher_key.decode(),
                                secret_encrypted,
                                passphrase_encrypted, auto_delete_id)

    result = SecretKey.model_validate({"key": cipher_key.decode()})

    return result


@router.get("/secret/{secret_key}")
async def get_secret(
    secret: Annotated[SecretKey, Depends()]
) -> SecretGenerate:
    key = secret.model_dump()["key"]

    async with asyncpg.create_pool(DATABASE_URL) as conn:
        await SecretsDAL(conn).delete_expired_secrets()

        if await SecretsDAL(conn).key_is_used(key):
            raise HTTPException(
                status_code=404,
                detail="The secret has already been read")

        secret_encrypted = await SecretsDAL(conn).get_encrypted_secret(key)
        passphrase_encrypted = (await SecretsDAL(conn).
                                get_encrypted_passphrase(key))

        await SecretsDAL(conn).update_is_used(key)

    # decryption of encrypted data received from the user
    decrypted_secret = await decrypt(key, secret_encrypted)
    decrypted_passphrase = await decrypt(key, passphrase_encrypted)

    result = SecretGenerate.model_validate({
        "secret_text": decrypted_secret,
        "passphrase": decrypted_passphrase,
        "key": key
    })

    return result


async def decrypt(key: str, secret_encrypted: str) -> str:
    """This handler decrypts encrypted data received from the user"""
    key_bytes = key.encode()

    cipher = Fernet(key_bytes)
    decrypted_secret = cipher.decrypt(secret_encrypted.encode())

    return decrypted_secret


async def encrypt(key: bytes, secret_text: str) -> str:
    """This handler encrypts the data received from the user"""
    cipher = Fernet(key)

    secret_encrypted_bytes = cipher.encrypt(secret_text.encode())
    secret_encrypted = secret_encrypted_bytes.decode()

    return secret_encrypted
