from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def registor_middleware(app: FastAPI):
    
    # 1. Pehle CORS add karein (Ye sabse bahar hona chahiye)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "localhost", 
        "127.0.0.1", 
        "api-backend-nkgk.onrender.com",  # 'https://' aur trailing '/' hata dein
        "*.onrender.com"                  # Backup ke liye wildcard
    ]
)

    # 2. Custom Logging Middleware
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        processsing_time = time.time() - start_time
        message = f"{request.client.host} : {request.client.port} {request.method} - {request.url.path} - {response.status_code} completed after {processsing_time}s"
        print(message)
        return response

    # 3. Authorization Middleware (Isme OPTIONS check zaroori hai)
    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     # CORS Preflight (OPTIONS) requests ko allow karna zaroori hai
    #     if request.method == "OPTIONS":
    #         return await call_next(request)

    #     # Auth Check
    #     if "Authorization" not in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not Authenticated",
    #                 "resolution": "Please provide the right credentials to proceed",
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #         )
        
    #     response = await call_next(request)
    #     return response