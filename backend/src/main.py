from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import claims
import logging

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .rate_limiter import limiter

app = FastAPI(title="Plum Claims Engine")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://neural-plum.pages.dev", 
        "https://neural-plum-app.vercel.app", 
        "http://localhost:5173"
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(claims.router)

@app.get("/")
def read_root():
    return {"status": "Neural Plum API is running!", "docs": "/docs"}
