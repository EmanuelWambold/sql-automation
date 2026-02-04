import os
import psycopg2
from dotenv import load_dotenv

# Open .env
load_dotenv()

# --- DB Connection helper ---
def require_env(name: str, default: str | None = None) -> str:
    """
    This method safely gets the required environment variable or raises a clear error.
    
    Args:
        name (str): Environment variable name
        default (Optional str): Optional default value (if None, raises error)
    
    Returns:
        str: Environment variable value
    
    Raises:
        RuntimeError: if variable missing and no default provided
    """

    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_connection() -> "psycopg2.connection":
    """
    This method creates the database connection using the environment variables.
    
    Returns:
        psycopg2.connection: Active database connection
        
    Raises:
        RuntimeError: if required environment variables (DB_NAME, DB_USER, DB_PASSWORD) are missing
        ValueError: if DB_PORT is invalid
        psycopg2.OperationalError: if database connection fails
    """

    return psycopg2.connect(
        dbname=require_env("DB_NAME"),
        user=require_env("DB_USER"),
        password=require_env("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432))
    )