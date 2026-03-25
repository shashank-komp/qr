import os
from pathlib import Path
 
from dotenv import load_dotenv
 
 
def configure_django_environment() -> str:
    ENV = os.getenv("ENVIRONMENT", "dev").lower()
    BASE_DIR = Path(__file__).resolve().parent.parent
 
    env_file = BASE_DIR / f".env.{ENV}"
    if env_file.exists():
        load_dotenv(env_file)
 
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"core.settings.{ENV}")
    return str(ENV)
 