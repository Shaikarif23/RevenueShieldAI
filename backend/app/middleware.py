import time
from fastapi import FastAPI, Request


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def log_requests(request: Request, call_next):

        start_time = time.time()

        response = await call_next(request)

        process_time = round(time.time() - start_time, 3)

        print(
            f"[{request.method}] "
            f"{request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time}s"
        )

        return response
