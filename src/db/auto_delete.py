import logging
from asyncpg import Connection
from uuid import uuid4


class AutoDeleteDAL:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        self.logger = logging.getLogger("autodelete_dal")

    async def get_id(self, auto_delete_value: str) -> uuid4:
        """
        Gets the ID of the secret lifetime by its name

        Args:
            auto_delete_value (str): the name of the lifetime

        Returns:
            id (uuid): ID of the secret lifetime
        """

        id: uuid4 = await self.connection.fetchval(
            "SELECT id FROM auto_delete WHERE delete_name = $1",
            auto_delete_value
        )

        return id
