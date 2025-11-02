from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str | None = None
    OSRM_SERVER_URL: str = "http://localhost:5000"
    SIMULATION_SPEED: float = 1.0
    MAX_DRIVERS: int = 4
    DRIVER_SPEED_MPS: float = 10.0  # simulated meters per second for movement

    class Config:
        env_file = ".env"


settings = Settings()