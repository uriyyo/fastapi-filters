from pydantic_settings import BaseSettings, SettingsConfigDict


class FastAPIFiltersSettings(BaseSettings):
    csv_separator: str = ","
    model_config = SettingsConfigDict(env_prefix="FASTAPI_FILTERS_", env_file=".env")


app_settings = FastAPIFiltersSettings()
