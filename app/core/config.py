from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ecom Watch Agent Demo"
    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8005
    database_url: str = "sqlite:///data/app.db"
    mock_state_file: str = "data/mock_pages/state.txt"
    screenshots_dir: str = "data/screenshots"
    mock_pages_dir: str = "data/mock_pages"
    llm_enabled: bool = False
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    feishu_webhook_url: str = ""
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_enable_app_bot: bool = False
    feishu_default_chat_id: str = ""
    feishu_default_open_id: str = ""
    feishu_use_demo_last_run: bool = True
    feishu_enable_send: bool = False
    enable_discovery: bool = False
    searxng_base_url: str = ""
    searxng_timeout: int = 8
    searxng_default_limit: int = 10
    searxng_allowed_domains: str = ""
    enable_scrapy: bool = False
    scrapy_default_source: str = "fixture"
    scrapy_fixture_dir: str = "data/fixtures"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def mock_state_path(self) -> Path:
        return self.base_dir / self.mock_state_file

    @property
    def screenshots_path(self) -> Path:
        return self.base_dir / self.screenshots_dir

    @property
    def mock_pages_path(self) -> Path:
        return self.base_dir / self.mock_pages_dir

    @property
    def searxng_allowed_domains_list(self) -> list[str]:
        if not self.searxng_allowed_domains.strip():
            return []
        return [item.strip().lower() for item in self.searxng_allowed_domains.split(",") if item.strip()]

    @property
    def scrapy_fixture_path(self) -> Path:
        return self.base_dir / self.scrapy_fixture_dir


settings = Settings()
