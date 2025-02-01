from fastapi import FastAPI
import uvicorn
from core.configs import settings
from api.v1.api import api_router


app = FastAPI(title='Cursos API - FastAPI SQL Alchemy')
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == '__main__':
    

    uvicorn.run("main:app", host="0.0.0.0", port=3232, log_level='info', reload=True)
