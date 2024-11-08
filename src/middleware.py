from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_requests: int, time_window: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Удаление устаревших временных меток
        timestamps = self.request_counts[client_ip]
        self.request_counts[client_ip] = [
            timestamp for timestamp in timestamps
            if current_time - timestamp < self.time_window
            ]

        # Проверка лимита запросов
        if len(self.request_counts[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Too Many Requests")

        # Добавление текущего запроса
        self.request_counts[client_ip].append(current_time)

        response = await call_next(request)
        return response
