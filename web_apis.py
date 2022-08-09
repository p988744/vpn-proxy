import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from db import models
from db.database import engine, SessionLocal
from service.routers import api_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    contact={
        "name": "eLand Information",
        "url": "https://eland.com.tw",
        "email": "service@eland.com.tw",
        "phone": "886-2-2755-1533"
    },
    version='v1.0 beta1',
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    redoc_url='/redoc',
    docs_url='/'
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"]
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app="web_apis:app", host="0.0.0.0", port=8080, reload=True)
