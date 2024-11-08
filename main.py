from fastapi import FastAPI
from src.router import router as secret_router
import uvicorn
from src.middleware import RateLimitMiddleware
from src.db.secrets import SecretsDAL
import asyncpg
from contextlib import asynccontextmanager
from config.config import DATABASE_URL


app = FastAPI()
app.include_router(secret_router)
# request limit (600 requests per minute)
app.add_middleware(RateLimitMiddleware, max_requests=600, time_window=60)

main_app_lifespan = app.router.lifespan_context


@asynccontextmanager
async def lifespan_wrapper(app):
    async with asyncpg.create_pool(DATABASE_URL) as conn:
        await SecretsDAL(conn).create_tables()
    async with main_app_lifespan(app) as maybe_state:
        yield maybe_state
app.router.lifespan_context = lifespan_wrapper


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0")
