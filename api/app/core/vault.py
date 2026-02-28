import httpx
import uuid
import os
import logging

logger = logging.getLogger(__name__)

DEVICE_IDENTIFIER = str(uuid.uuid4())

async def get_vault_token(vault_url: str, client_id: str, client_secret: str) -> str:
    async with httpx.AsyncClient(verify=True) as client:
        response = await client.post(
            f"{vault_url}/identity/connect/token",
            data={
                "grant_type":        "client_credentials",
                "client_id":         client_id,
                "client_secret":     client_secret,
                "scope":             "api",
                "device_type":       "21",
                "device_identifier": DEVICE_IDENTIFIER,
                "device_name":       "sentineledge-api",
            }
        )
        response.raise_for_status()
        return response.json()["access_token"]


async def get_vault_secrets(vault_url: str, token: str) -> dict:
    async with httpx.AsyncClient(verify=True) as client:
        response = await client.get(
            f"{vault_url}/api/sync",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        data = response.json()

    secrets = {}

    # Vaultwarden returns lowercase "ciphers"
    ciphers = data.get("ciphers", data.get("Ciphers", []))
    logger.info(f"Total ciphers found: {len(ciphers)}")

    for cipher in ciphers:
        if cipher.get("type", cipher.get("Type")) != 1:
            continue

        name = cipher.get("name", cipher.get("Name", ""))

        # Try login.password first, then data.password
        login = cipher.get("login", cipher.get("Login")) or {}
        password = login.get("password", login.get("Password", ""))

        if not password:
            data_field = cipher.get("data") or {}
            password = data_field.get("password", "")

        if name and password and not name.startswith("2."):
            secrets[name] = password
            logger.info(f"  -> Loaded secret: {name}")

    return secrets


async def load_secrets_from_vault() -> dict:
    vault_url     = os.getenv("VAULT_URL", "")
    client_id     = os.getenv("VAULT_CLIENT_ID", "")
    client_secret = os.getenv("VAULT_CLIENT_SECRET", "")

    if not all([vault_url, client_id, client_secret]):
        logger.warning("Vault credentials not set — skipping vault load")
        return {}

    try:
        logger.info(f"Connecting to Vaultwarden at {vault_url}...")
        token   = await get_vault_token(vault_url, client_id, client_secret)
        secrets = await get_vault_secrets(vault_url, token)
        logger.info(f"Loaded {len(secrets)} secrets from Vaultwarden")

        for key, value in secrets.items():
            os.environ[key] = value

        return secrets
    except Exception as e:
        logger.error(f"Failed to load secrets from Vaultwarden: {e}")
        raise