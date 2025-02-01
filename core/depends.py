from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from jose import jwt, JWTError

from core.database import Session
from core.auth import oauth2_schema
from core.configs import settings
from models.usuario_model import UsuarioModel


# define o metodos de depedencia das requisições

class TokenData(BaseModel):
    user_id: Optional[str] = None


async def get_session()-> Generator: # dependencia de sessão de conexão com o banco de dados
    session: AsyncSession = Session()
    
    try:
        yield session # retorna o estado atual da session
    finally:
        await session.close() # encerra a session


# 
async def get_current_user(db: Session = Depends(get_session), token:str = Depends(oauth2_schema))->UsuarioModel:
    
    # objeto de exceção de unauthorized
    credential_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar a credencial.",
        headers={"WWWW-Authenticate:":"Bearer"}
    )


    try:
        payload = jwt.decode( # descriptografa o payload
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud":False}
        )
        
        user_id: str = payload.get("sub") # id do usuario
        
        if user_id is None:
            raise credential_exception
        
        token_data = TokenData(user_id)
                
    except JWTError:
        raise credential_exception
    
    
    # consulta o usuario no banco de dados 
    async with db as session:
        query = select(UsuarioModel.filter(UsuarioModel.id == int(token_data.user_id)))
        result = await session.execute(query)
        usuario: UsuarioModel = result.scalars().unique().one_or_none()
        
        if usuario is None:
            raise credential_exception
        
        return usuario