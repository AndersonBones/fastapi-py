from typing import List
from pydantic import AnyHttpUrl, BaseSettings
from sqlalchemy.ext.declarative import declarative_base


class Settings(BaseSettings):
    
    """
    Configurações gerais uasadas na aplicação
    """
    
    API_V1_STR:str = '/api/v1' # base url
    DB_URL:str = "postgresql+asyncpg://postgres:root1234@127.0.0.1:5432/faculdade" # url de conexão com banco de dados
    DBBaseModel = declarative_base()
    
    JWT_SECRET: str = 'DNx40SQ04ngu3W10ynt9-mM7YcDj6DEU4VyRp6lsexg'
    ALGORITHM: str = 'HS256'
    
    # 60min * 24h * 7d => 1 week
    ACESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    

    class Config:
        case_sensitive = True # 



settings: Settings = Settings()
