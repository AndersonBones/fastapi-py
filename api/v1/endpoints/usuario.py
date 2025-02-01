from typing import List, Optional, Any

from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioSchemaBase, UsuarioSchemaCreate, UsuarioSchemaArtigos, UsuarioSchemaUp
from core.depends import get_session, get_current_user
from core.security import gerar_hash_senha
from core.auth import autenticar, criar_token_acesso



router = APIRouter() # instancia da classe APIRouter

# Rota para retornar os dados do usuario logado
@router.get("/logado", response_model=UsuarioSchemaBase)
def get_logado(usuario_logado: UsuarioModel = Depends(get_current_user)):
    return usuario_logado


# POST / Signup - Registra um novo usuario no banco de dados
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UsuarioSchemaBase)
async def post_usuario(usuario: UsuarioSchemaCreate, db: AsyncSession = Depends(get_session)):
    
   
   # cria o objeto com os dados do usuario informados no corpo da requisição
    novo_usuario: UsuarioModel = UsuarioModel(
        nome=usuario.nome, 
        sobrenome=usuario.sobrenome, 
        email=usuario.email,
        senha=gerar_hash_senha(usuario.senha), # gera o hash da senha
        admin=usuario.admin # define se o usuario é administrador ou não
    )
    
    async with db as session: 
        try:
            session.add(novo_usuario) # adiciona um novo usuario no banco dedados
            await session.commit() # persiste os dados no banco
            
            return novo_usuario # retorna os dados do novo usuario
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="user already exists.")
            


# GET Usuarios - retorna todos os usuarios do banco de dados
@router.get("/", response_model=List[UsuarioSchemaBase])
async def get_usuarios(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel) # consulta no banco de dados
        result = await session.execute(query) # executa a consulta no banco de dados
        usuarios: List[UsuarioSchemaBase] = result.scalars().unique().all() # obtém a lista de usuarios
        
        return usuarios # retorna a lista de usuários


# GET Usuario - retorna um usuario especifico 
@router.get("/{usuario_id}", response_model=UsuarioSchemaArtigos, status_code=status.HTTP_200_OK)
async def get_usuario(usuario_id: int, db:AsyncSession = Depends(get_session)):
    
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == usuario_id) # consulta com base no id informado na query da requsição
        result = await session.execute(query) # executa a consulta
        usuario: UsuarioSchemaArtigos = result.scalars().unique().one_or_none() # obtém o usuario
        
        if usuario is None:
            raise HTTPException(detail="Usuário não encontrado.", status_code=status.HTTP_404_NOT_FOUND)
        
        return usuario

# PUT Usuario
@router.put("/{usuario_id}", response_model=UsuarioSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def get_usuario(usuario_id: int, usuario: UsuarioSchemaUp,db:AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == usuario_id)
        result = await session.execute(query)
        has_usuario: UsuarioSchemaBase = result.scalars().unique().one_or_none()
        
        
        if has_usuario:
            if usuario.nome:
                has_usuario.nome = usuario.nome
            if usuario.sobrenome:
                has_usuario.sobrenome = usuario.sobrenome
            if usuario.email:
                has_usuario.email = usuario.email
            if usuario.admin:
                has_usuario.admin = usuario.admin
            if usuario.senha:
                has_usuario.senha = gerar_hash_senha(usuario.senha)
                
            return has_usuario
        
        else:
            raise HTTPException(detail="Usuário não encontrado.", status_code=status.HTTP_404_NOT_FOUND)
        


@router.delete("/{usuario_id}", response_model=UsuarioSchemaArtigos, status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id: int, db:AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == usuario_id)
        result = await session.execute(query)
        usuario: UsuarioSchemaArtigos = result.scalars().unique().one_or_none()
        
        if usuario is None:
            raise HTTPException(detail="Usuário não encontrado.", status_code=status.HTTP_404_NOT_FOUND)
        
        await session.delete(usuario)
        await session.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    

# POST Login
@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    usuario = await autenticar(
        db=db,
        email=form_data.username,
        senha=form_data.password
    )
    
    if not usuario:
        raise HTTPException(detail="Dados de acesso incorretos.", status_code=status.HTTP_400_BAD_REQUEST)
    
   
    content = {
        "access_token":criar_token_acesso(sub=usuario.id),
        "token_type":"bearer"
    }
    
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)