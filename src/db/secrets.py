import logging
from asyncpg import Connection
from asyncpg.exceptions import PostgresError
from fastapi import HTTPException
from uuid import uuid4


class SecretsDAL:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        self.logger = logging.getLogger("secrets_dal")

    async def insert_secret(self, key: str,
                            secret: str,
                            passphrase: str,
                            auto_delete_id: uuid4) -> None:
        """
        Adds the secret entered by the user to the database

        Args:
            key (str): id of new secret.
            secret (str): secret entered by the user
            passphrase (str): passphrase entered by the user
            auto_delete_id (uuid): ID of the time of life

        Returns:
            None
        """

        try:
            await self.connection.execute(
                """INSERT INTO Secrets
                    (key, secret_encrypted, passphrase_encrypted,
                    auto_delete_id)
                    VALUES ($1, $2, $3, $4)""",
                key, secret, passphrase, auto_delete_id)

        except PostgresError as e:
            raise Exception(f"""Error {e} when trying to load
                                the following data into the table Secrets:
                                key: {key},
                                secret: {secret},
                                passphrase: {passphrase}""")

    async def get_encrypted_secret(self, key: str) -> str | None:
        """
        Retrieves the encrypted secret from the database

        Args:
            key (str): id of secret.

        Returns:
            secret_encrypted (str | None): encrypted secret
        """

        secret_encrypted: str | None = await self.connection.fetchval(
            "SELECT secret_encrypted FROM Secrets WHERE key = $1", key
        )

        if not secret_encrypted:
            raise HTTPException(status_code=404, detail="There is no such key")

        return secret_encrypted

    async def get_encrypted_passphrase(self, key: str) -> str | None:
        """
        Retrieves the encrypted passphrase from the database

        Args:
            key (str): id of secret.

        Returns:
            passphrase_encrypted (str | None): encrypted passphrase
        """

        passphrase_encrypted: str | None = await self.connection.fetchval(
            "SELECT passphrase_encrypted FROM Secrets WHERE key = $1", key
        )

        if not passphrase_encrypted:
            raise HTTPException(status_code=404, detail="There is no such key")

        return passphrase_encrypted

    async def update_is_used(self, key: str) -> None:
        """
        Notifies the database that the secret has already been used

        Args:
            key (str): id of secret.

        Returns:
            None
        """

        query = "UPDATE Secrets SET is_used = True WHERE key = $1"
        await self.connection.execute(query, key)

    async def key_is_used(self, key: str) -> bool:
        """
        Finds out if the secret was used

        Args:
            key (str): id of secret.

        Returns:
            is_used (bool): True if the secret was used False otherwise
        """

        query = "SELECT is_used FROM Secrets WHERE key = $1"
        is_used: bool = await self.connection.fetchval(query, key)

        return is_used

    async def delete_expired_secrets(self) -> None:
        """
        Deletes all secrets that have expired

        Args:
            None

        Returns:
            None
        """

        sql = """
            DELETE FROM
            secrets
                USING
            auto_delete
                WHERE
            secrets.auto_delete_id = auto_delete.id
            AND secrets.Insdate +
            (CASE
                WHEN delete_name = '5 days' THEN interval '5 days'
                WHEN delete_name = '1 hour' THEN interval '1 hour'
                WHEN delete_name = '1 min' THEN interval '1 minute'
                ELSE interval '0 days'
            END) <= NOW()
        """
        try:
            await self.connection.execute(sql)
        except PostgresError as e:
            raise Exception(f'Error deleting a secret {e}')

    async def create_tables(self):
        sql = """
            SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'auto_delete'
            ) AS table_exists;
        """
        auto_delete_is_used: bool = await self.connection.fetchval(sql)

        if not auto_delete_is_used:
            sql = """
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

                CREATE TABLE auto_delete (
                    id uuid not null DEFAULT uuid_generate_v4() PRIMARY KEY,
                    delete_name varchar(64),
                    InsDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );

                INSERT INTO auto_delete
                (delete_name)
                VALUES
                ('1 hour'),
                ('5 days'),
                ('1 min'),
                (NULL)
            """
            try:
                await self.connection.execute(sql)
            except PostgresError as e:
                raise Exception(f"""Error when trying to create a
                                table auto_delete: {e}""")

        sql = """
            SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'secrets'
            ) AS table_exists;
        """
        secrets_is_exist: bool = await self.connection.fetchval(sql)

        if not secrets_is_exist:
            sql = """
                CREATE TABLE Secrets (
                    key varchar(64) PRIMARY KEY,
                    secret_encrypted text,
                    passphrase_encrypted text,
                    auto_delete_id uuid REFERENCES auto_delete (id),
                    is_used boolean NOT NULL DEFAULT false,
                    InsDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """
            try:
                await self.connection.execute(sql)
            except PostgresError as e:
                raise Exception(f"""Error when trying to create
                                a table secrets: {e}""")
