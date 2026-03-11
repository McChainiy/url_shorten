from unittest.mock import MagicMock
from src.utils.link_service import LinkService
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
import pytest


def test_get_user_type_authenticated():
    user = MagicMock()
    user_type = LinkService.get_user_type(user)

    assert user_type == "authenticated"

def test_validate_expiry_default_anonymous():
    result = LinkService.validate_expiry_date(None, None)
    now = datetime.now(timezone.utc)
    delta = result - now

    assert 6 <= delta.days <= 7

def test_expiry_too_far():
    expires = datetime.now(timezone.utc) + timedelta(days=20)

    with pytest.raises(HTTPException):
        LinkService.validate_expiry_date(expires, None)