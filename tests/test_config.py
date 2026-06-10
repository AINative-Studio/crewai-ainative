"""
Tests for crewai-ainative configuration.

Refs #3952
"""

import json
import os
from unittest.mock import patch, MagicMock

import pytest

from crewai_ainative.config import (
    configure_crew,
    get_llm_config,
    get_memory_config,
    get_model,
    MODELS,
    DEFAULT_MODEL,
    API_BASE,
    MEMORY_API_BASE,
)
from crewai_ainative.provision import (
    resolve_api_key,
    _load_credentials,
    _auto_provision,
    _save_credentials,
    ZERODB_DIR,
    CREDS_PATH,
    CONFIG_PATH,
)


# ---------------------------------------------------------------------------
# Model resolution
# ---------------------------------------------------------------------------

class TestGetModel:
    """Tests for model alias resolution."""

    def test_llama_alias(self):
        assert get_model("llama") == "meta-llama/Llama-3.3-70B-Instruct"

    def test_qwen_alias(self):
        assert get_model("qwen") == "qwen3-coder-flash"

    def test_deepseek_alias(self):
        assert get_model("deepseek") == "deepseek-4-flash"

    def test_kimi_alias(self):
        assert get_model("kimi") == "kimi-k2"

    def test_passthrough_full_id(self):
        assert get_model("meta-llama/Llama-3.3-70B-Instruct") == "meta-llama/Llama-3.3-70B-Instruct"

    def test_unknown_returns_as_is(self):
        assert get_model("custom-model") == "custom-model"


# ---------------------------------------------------------------------------
# LLM config
# ---------------------------------------------------------------------------

class TestGetLlmConfig:
    """Tests for LLM config generation."""

    @patch("crewai_ainative.config.resolve_api_key", return_value="test-key")
    def test_default_config(self, mock_resolve):
        config = get_llm_config()
        assert config["OPENAI_API_KEY"] == "test-key"
        assert config["OPENAI_API_BASE"] == API_BASE
        assert config["OPENAI_MODEL_NAME"] == DEFAULT_MODEL

    @patch("crewai_ainative.config.resolve_api_key", return_value="test-key")
    def test_custom_model(self, mock_resolve):
        config = get_llm_config(model="qwen")
        assert config["OPENAI_MODEL_NAME"] == "qwen3-coder-flash"

    @patch("crewai_ainative.config.resolve_api_key", return_value="test-key")
    def test_custom_base(self, mock_resolve):
        config = get_llm_config(api_base="https://custom.api/v1")
        assert config["OPENAI_API_BASE"] == "https://custom.api/v1"

    @patch("crewai_ainative.config.resolve_api_key", return_value="explicit-key")
    def test_explicit_key(self, mock_resolve):
        config = get_llm_config(api_key="explicit-key")
        assert config["OPENAI_API_KEY"] == "explicit-key"


# ---------------------------------------------------------------------------
# Memory config
# ---------------------------------------------------------------------------

class TestGetMemoryConfig:
    """Tests for ZeroMemory config generation."""

    @patch("crewai_ainative.config.resolve_api_key", return_value="mem-key")
    def test_default_memory_config(self, mock_resolve):
        config = get_memory_config()
        assert config["memory_api_base"] == MEMORY_API_BASE
        assert config["api_key"] == "mem-key"
        assert config["entity"] == "crewai-agent"

    @patch("crewai_ainative.config.resolve_api_key", return_value="mem-key")
    def test_custom_entity(self, mock_resolve):
        config = get_memory_config(entity="my-crew")
        assert config["entity"] == "my-crew"


# ---------------------------------------------------------------------------
# configure_crew
# ---------------------------------------------------------------------------

class TestConfigureCrew:
    """Tests for the main configure_crew() function."""

    @patch("crewai_ainative.config.resolve_api_key", return_value="crew-key-1234567890")
    def test_sets_env_vars(self, mock_resolve):
        with patch.dict(os.environ, {}, clear=False):
            result = configure_crew(verbose=False)
            assert result == "crew-key-1234567890"
            assert os.environ["OPENAI_API_KEY"] == "crew-key-1234567890"
            assert os.environ["OPENAI_API_BASE"] == API_BASE
            assert os.environ["OPENAI_MODEL_NAME"] == DEFAULT_MODEL
            assert os.environ["AINATIVE_API_KEY"] == "crew-key-1234567890"

    @patch("crewai_ainative.config.resolve_api_key", return_value="crew-key-1234567890")
    def test_sets_custom_model(self, mock_resolve):
        with patch.dict(os.environ, {}, clear=False):
            configure_crew(model="deepseek", verbose=False)
            assert os.environ["OPENAI_MODEL_NAME"] == "deepseek-4-flash"

    @patch("crewai_ainative.config.resolve_api_key", return_value="crew-key-1234567890")
    def test_verbose_output(self, mock_resolve, capsys):
        configure_crew(verbose=True)
        captured = capsys.readouterr()
        assert "crewai-ainative configured" in captured.err

    @patch("crewai_ainative.config.resolve_api_key", return_value="crew-key-1234567890")
    def test_returns_api_key(self, mock_resolve):
        result = configure_crew(verbose=False)
        assert result == "crew-key-1234567890"


# ---------------------------------------------------------------------------
# API key resolution
# ---------------------------------------------------------------------------

class TestResolveApiKey:
    """Tests for the multi-source API key resolution."""

    def test_explicit_key_takes_priority(self):
        result = resolve_api_key(explicit_key="explicit-key")
        assert result == "explicit-key"

    @patch.dict(os.environ, {"AINATIVE_API_KEY": "env-key"}, clear=False)
    def test_ainative_env_var(self):
        result = resolve_api_key()
        assert result == "env-key"

    @patch.dict(os.environ, {"ZERODB_API_KEY": "zerodb-key"}, clear=False)
    def test_zerodb_env_var(self):
        env = os.environ.copy()
        env.pop("AINATIVE_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            os.environ["ZERODB_API_KEY"] = "zerodb-key"
            result = resolve_api_key()
            assert result == "zerodb-key"

    @patch.dict(os.environ, {"AINATIVE_API_KEY": "ainative", "ZERODB_API_KEY": "zerodb"}, clear=False)
    def test_ainative_key_preferred_over_zerodb(self):
        result = resolve_api_key()
        assert result == "ainative"


# ---------------------------------------------------------------------------
# Credential file loading
# ---------------------------------------------------------------------------

class TestLoadCredentials:
    """Tests for credential file loading."""

    def test_returns_none_when_no_files(self, tmp_path):
        with patch("crewai_ainative.provision.CREDS_PATH", tmp_path / "missing.json"):
            with patch("crewai_ainative.provision.CONFIG_PATH", tmp_path / "missing2.json"):
                result = _load_credentials()
                assert result is None

    def test_reads_credentials_json(self, tmp_path):
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text(json.dumps({"api_key": "file-key"}))

        with patch("crewai_ainative.provision.CREDS_PATH", creds_file):
            with patch("crewai_ainative.provision.CONFIG_PATH", tmp_path / "missing.json"):
                result = _load_credentials()
                assert result == "file-key"

    def test_handles_corrupt_json(self, tmp_path):
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("not valid json{{{")

        with patch("crewai_ainative.provision.CREDS_PATH", creds_file):
            with patch("crewai_ainative.provision.CONFIG_PATH", tmp_path / "missing.json"):
                result = _load_credentials()
                assert result is None


# ---------------------------------------------------------------------------
# Auto-provisioning
# ---------------------------------------------------------------------------

class TestAutoProvision:
    """Tests for the auto-provisioning endpoint."""

    @patch("crewai_ainative.provision.requests")
    @patch("crewai_ainative.provision._save_credentials")
    @patch("crewai_ainative.provision._print_success")
    def test_successful_provision(self, mock_print, mock_save, mock_requests):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "api_key": "new-key-12345678",
            "project_id": "proj-1",
            "claim_url": "https://ainative.studio/claim/abc",
        }
        mock_requests.post.return_value = mock_resp

        result = _auto_provision()

        assert result == "new-key-12345678"
        mock_save.assert_called_once()
        mock_print.assert_called_once()

    @patch("crewai_ainative.provision.requests")
    def test_rate_limited(self, mock_requests):
        import requests as real_requests
        mock_requests.RequestException = real_requests.RequestException
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_requests.post.return_value = mock_resp

        with pytest.raises(RuntimeError, match="Rate limited"):
            _auto_provision()

    @patch("crewai_ainative.provision.requests")
    def test_server_error(self, mock_requests):
        import requests as real_requests
        mock_requests.RequestException = real_requests.RequestException
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_requests.post.return_value = mock_resp

        with pytest.raises(RuntimeError, match="Provisioning failed"):
            _auto_provision()

    @patch("crewai_ainative.provision.requests")
    def test_empty_api_key(self, mock_requests):
        import requests as real_requests
        mock_requests.RequestException = real_requests.RequestException
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"api_key": ""}
        mock_requests.post.return_value = mock_resp

        with pytest.raises(RuntimeError, match="empty API key"):
            _auto_provision()

    @patch("crewai_ainative.provision.requests")
    def test_network_error(self, mock_requests):
        import requests as real_requests
        mock_requests.RequestException = real_requests.RequestException
        mock_requests.post.side_effect = real_requests.ConnectionError("fail")

        with pytest.raises(RuntimeError, match="Network error"):
            _auto_provision()


# ---------------------------------------------------------------------------
# Credential persistence
# ---------------------------------------------------------------------------

class TestSaveCredentials:
    """Tests for credential persistence."""

    def test_saves_to_file(self, tmp_path):
        creds_dir = tmp_path / ".zerodb"
        creds_path = creds_dir / "credentials.json"

        with patch("crewai_ainative.provision.ZERODB_DIR", creds_dir):
            with patch("crewai_ainative.provision.CREDS_PATH", creds_path):
                _save_credentials({
                    "api_key": "saved-key",
                    "project_id": "proj-1",
                    "claim_url": "https://ainative.studio/claim/abc",
                })

        assert creds_path.exists()
        data = json.loads(creds_path.read_text())
        assert data["api_key"] == "saved-key"
        assert data["source"] == "crewai-ainative"
