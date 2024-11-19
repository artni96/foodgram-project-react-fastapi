from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL"]
    DB_NAME: str
    DB_HOST: str
    DB_USER: str
    DB_USER_PASSWORD: str
    DB_PORT: int
    SECRET_KEY: str

    @property
    def DB_URL(self) -> str:
        url = (
            f'postgresql+asyncpg://{self.DB_USER}:'
            f'{self.DB_USER_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/'
            f'{self.DB_NAME}'
        )
        return url

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
