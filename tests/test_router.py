import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.router import router


# Создайте FastAPI приложение для тестирования
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_generate_secret_key(client):
    secret_data = {
        "secret_text": "my_secret",
        "passphrase": "my_passphrase",
        "auto_delete": "auto_delete"
    }

    # Mocking dependencies
    with patch('SecretsDAL') as MockSecretsDAL, \
         patch('AutoDeleteDAL') as MockAutoDeleteDAL:

        mock_secrets_dal = AsyncMock()
        mock_auto_delete_dal = AsyncMock()

        MockSecretsDAL.return_value = mock_secrets_dal
        MockAutoDeleteDAL.return_value = mock_auto_delete_dal
        mock_auto_delete_dal.get_id.return_value = AsyncMock(return_value=1)
        mock_secrets_dal.delete_expired_secrets.return_value = None

        response = await client.post("/generate", json=secret_data)

        assert response.status_code == 200
        assert "key" in response.json()


@pytest.mark.asyncio
async def test_get_secret(client):
    secret_key = "some_generated_key"

    # Mocking dependencies
    with patch('SecretsDAL') as MockSecretsDAL:
        mock_secrets_dal = AsyncMock()
        MockSecretsDAL.return_value = mock_secrets_dal

        # Mocking methods to return sample data
        mock_secrets_dal.key_is_used.return_value = AsyncMock(
            return_value=False)
        mock_secrets_dal.get_encrypted_secret.return_value = AsyncMock(
            return_value="encrypted_secret")
        mock_secrets_dal.get_encrypted_passphrase.return_value = AsyncMock(
            return_value="encrypted_passphrase")
        mock_secrets_dal.update_is_used.return_value = None

        # Here we could also mock the decrypt method to
        # simulate decryption results
        with patch('decrypt') as mock_decrypt:
            mock_decrypt.side_effect = (lambda k, v: "decrypted_text"
                                        if v == "encrypted_secret"
                                        else "decrypted_passphrase")

            response = await client.get(f"/secret/{secret_key}",
                                        params={"key": secret_key})

            assert response.status_code == 200
            assert response.json()["secret_text"] == "decrypted_text"
            assert response.json()["passphrase"] == "decrypted_passphrase"
            assert response.json()["key"] == secret_key


@pytest.mark.asyncio
async def test_get_secret_already_used(client):
    secret_key = "used_secret_key"

    # Mocking dependencies
    with patch('SecretsDAL') as MockSecretsDAL:
        mock_secrets_dal = AsyncMock()
        MockSecretsDAL.return_value = mock_secrets_dal

        mock_secrets_dal.key_is_used.return_value = AsyncMock(
            return_value=True)

        response = await client.get(f"/secret/{secret_key}",
                                    params={"key": secret_key})

        assert response.status_code == 404
        assert response.json()["detail"] == "The secret has already been read"
