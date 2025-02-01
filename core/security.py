from passlib.context import CryptContext


CRYPT = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verificar_senha(senha: str, hash_senha: str)-> bool:
    """
        Função para verificar se a senha esta correta, realiza uma comparação entre a hash 
        salva no banco de dados e a senha informada.
    """
    
    return CRYPT.verify(senha, hash_senha)
    

def gerar_hash_senha(senha: str)->str:
    """
        Função que gera e retorna o hash da senha informa pelo usuário.
    """
    
    return CRYPT.hash(senha)
