from pydantic import BaseModel
from typing import Literal


class SecretCodeAdd(BaseModel):
    secret_text: str
    passphrase: str
    auto_delete: Literal['1 hour', '5 days', '-', '1 min'] = '-'


class SecretKey(BaseModel):
    key: str


class SecretGenerate(SecretCodeAdd, SecretKey):
    pass


class Error(BaseModel):
    status: bool
    message: str
