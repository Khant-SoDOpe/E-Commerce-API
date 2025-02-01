from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from public import router as public_router

app = FastAPI()

# Include the routers from auth and public
app.include_router(auth_router, prefix="/auth")
app.include_router(public_router, prefix="/public")