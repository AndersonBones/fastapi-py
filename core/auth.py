from pytz import timezone

from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt
from models.usuario_model import UsuarioModel
from core.configs import settings
from core.security import verificar_senha



oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/usuarios/login"
)


# verifica se o usuario esta logado 
async def autenticar(email: str, senha: str, db:AsyncSession) -> Optional[UsuarioModel]:
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.email == email) # realiza uma consulta pelo email
        result = await session.execute(query) # resultado da consulta
        usuario: UsuarioModel = result.scalars().unique().one_or_none() # retorna um usuario
        
        # verifica se o usuario existe ou se a senha esta correta
        if not usuario or not verificar_senha(senha, usuario.senha): 
            return None
        
        return usuario
    

# cria o token
def criar_token(tipo_token:str, validade: timedelta, sub: str)->str:
    
    # cria o payload para encriptar ao token
    mt = timezone('America/Mato_Grosso')
    expira = datetime.now(tz=mt) + validade
    
    payload = {
        "type":tipo_token,
        "exp":expira,
        "iat":datetime.now(tz=mt),
        "sub":str(sub)
    }
    
    # cria e retorna o token utilizando o payload, jwt secret, algoritmo de criptografia
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


# retorna o token de acesso
def criar_token_acesso(sub: str)->str:
    return criar_token(
        tipo_token="access_token",
        validade=timedelta(minutes=settings.ACESS_TOKEN_EXPIRE_MINUTES),
        sub=sub
    )