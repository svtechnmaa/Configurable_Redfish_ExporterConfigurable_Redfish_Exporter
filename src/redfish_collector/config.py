from pydantic import IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    host: IPvAnyAddress
    port: int
    template_dir: str
    data_dir: str
    
    class Config:
        env = ".env"