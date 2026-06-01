import pytest

from app.api.main import assert_safe_config
from app.core.config import Settings


def test_production_with_dev_auth_bypass_raises():
    s = Settings(app_env="production", dev_auth_bypass=True)
    with pytest.raises(RuntimeError, match="DEV_AUTH_BYPASS"):
        assert_safe_config(s)


def test_production_with_bypass_off_is_allowed():
    s = Settings(app_env="production", dev_auth_bypass=False)
    assert_safe_config(s)


def test_dev_with_bypass_on_is_allowed():
    s = Settings(app_env="dev", dev_auth_bypass=True)
    assert_safe_config(s)
