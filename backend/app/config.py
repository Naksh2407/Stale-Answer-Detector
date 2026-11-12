import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bifrost_url: str = os.getenv("BIFROST_URL", "http://localhost:8080/v1")
    bifrost_api_key: str = os.getenv("BIFROST_API_KEY", "")
    bifrost_model: str = os.getenv("BIFROST_MODEL", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    max_claims: int = int(os.getenv("MAX_CLAIMS_PER_ANSWER", "10"))
    max_searches: int = int(os.getenv("MAX_SEARCHES_PER_REQUEST", "10"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    cache_path: str = os.getenv("CACHE_DB_PATH", "./cache.sqlite")
    offline: bool = os.getenv("OFFLINE_MODE", "0") == "1"

settings = Settings()
