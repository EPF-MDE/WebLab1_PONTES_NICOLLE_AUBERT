from src.config import settings

def test_settings_loaded():
    assert settings.PROJECT_NAME == "Library Management System"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.DATABASE_URL.startswith("sqlite")
