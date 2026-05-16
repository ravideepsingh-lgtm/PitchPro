from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Data source
    excel_data_folder: str = ""
    
    # LLM Settings
    openai_api_key: str = ""
    openai_base_url: str = "https://imllm.intermesh.net/v1"
    openai_model: str = "openrouter/qwen/qwen3-32b"
    
    # App Settings
    max_concurrent_llm_calls: int = 5
    batch_size: int = 100
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
