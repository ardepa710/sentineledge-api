import uuid
import hashlib
import secrets

def generate_token() -> str:
    """Genera un token único y seguro para un agente"""
    return secrets.token_hex(32)

def generate_id() -> str:
    """Genera un UUID único"""
    return str(uuid.uuid4())

def hash_token(token: str) -> str:
    """Hash del token para almacenar en DB"""
    return hashlib.sha256(token.encode()).hexdigest()