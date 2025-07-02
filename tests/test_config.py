from unittest.mock import mock_open, patch

import yaml

from app.configs import config


def test_get_config_loads_yaml(monkeypatch):
    # Prepare a minimal valid config dict (only app and llm sections from YAML)
    config_dict = {
        "app": {
            "host": "127.0.0.1",
            "name": "TestApp",
            "description": "desc",
            "version": "0.1",
            "port": 8000,
            "log_level": "INFO",
        },
        "llm": {
            "stock_analyzer_prompt_path": "./prompt.md",
            "temperature": 0.5,
            "max_tokens": 100,
            "retry": 2,
        },
    }
    yaml_str = yaml.dump(config_dict)
    
    # Mock environment variables for shioaji and gemini
    env_vars = {
        "SHIOAJI_API_KEY": "test_shioaji_key",
        "SHIOAJI_API_SECRET": "test_shioaji_secret",
        "GEMINI_ENDPOINT": "https://test-gemini.googleapis.com",
        "GEMINI_API_KEY": "test_gemini_key",
        "GEMINI_MODEL": "gemini-2.0-flash"
    }
    
    # Patch open to return this YAML
    with patch("builtins.open", mock_open(read_data=yaml_str)):
        with patch.dict("os.environ", env_vars):
            # Patch os.getenv to force config path
            monkeypatch.setenv("CONFIG_PATH", "dummy.yaml")
            cfg = config.get_config()
            assert cfg.app.name == "TestApp"
            assert cfg.llm.temperature == 0.5
            assert cfg.shioaji.api_key == "test_shioaji_key"
            assert cfg.gemini.model == "gemini-2.0-flash"


def test_get_config_with_env_vars():
    """Test config loading with environment variable substitution using pydantic-settings."""
    config_dict = {
        "app": {
            "host": "127.0.0.1",
            "name": "TestApp",
            "description": "desc",
            "version": "0.1",
            "port": 8000,
            "log_level": "INFO",
        },
        "llm": {
            "stock_analyzer_prompt_path": "./prompt.md",
            "temperature": 0.5,
            "max_tokens": 100,
            "retry": 2,
        },
    }
    yaml_str = yaml.dump(config_dict)
    
    # Mock environment variables
    env_vars = {
        "SHIOAJI_API_KEY": "test_shioaji_key",
        "SHIOAJI_API_SECRET": "test_shioaji_secret", 
        "GEMINI_ENDPOINT": "https://test-gemini.googleapis.com",
        "GEMINI_API_KEY": "test_gemini_key",
        "GEMINI_MODEL": "gemini-2.0-flash"
    }
    
    with patch("builtins.open", mock_open(read_data=yaml_str)):
        with patch.dict("os.environ", env_vars):
            with patch("os.getenv") as mock_getenv:
                mock_getenv.return_value = "dummy.yaml"
                cfg = config.get_config()
                
                assert cfg.shioaji.api_key == "test_shioaji_key"
                assert cfg.shioaji.api_secret == "test_shioaji_secret"
                assert cfg.gemini.endpoint == "https://test-gemini.googleapis.com"
                assert cfg.gemini.api_key.get_secret_value() == "test_gemini_key"
                assert cfg.gemini.model == "gemini-2.0-flash"
