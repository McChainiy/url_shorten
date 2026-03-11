import pytest
from datetime import datetime, timedelta, timezone

from src.schemas.links import LinkCreate, LinkUpdate

def test_link_create_success():
    future_time = datetime.now(timezone.utc) + timedelta(days=1)

    link = LinkCreate(
        original_url="https://example.com",
        custom_alias="custom_link",
        expires_at=future_time,
    )

    assert str(link.original_url) == "https://example.com/"
    assert link.custom_alias == "custom_link"

def test_link_update_success():
    future_time = datetime.now(timezone.utc) + timedelta(days=1)

    link = LinkUpdate(
        original_url="https://example.com",
        expires_at=future_time,
    )

    assert str(link.original_url) == "https://example.com/"

def test_invalid_alias():
    with pytest.raises(ValueError):
        LinkCreate(
            original_url="https://example.com",
            custom_alias="invalid@alias",
        )

def test_alias_too_short():
    with pytest.raises(ValueError):
        LinkCreate(
            original_url="https://example.com",
            custom_alias="abc",
        )

def test_expires_without_timezone():
    dt = datetime.now() + timedelta(days=1)

    with pytest.raises(ValueError):
        LinkCreate(
            original_url="https://example.com",
            expires_at=dt,
        )
    with pytest.raises(ValueError):
        LinkUpdate(
            original_url="https://example.com",
            expires_at=dt,
        )


def test_expires_in_past():
    past = datetime.now(timezone.utc) - timedelta(days=1)

    with pytest.raises(ValueError):
        LinkCreate(
            original_url="https://example.com",
            expires_at=past,
        )
    with pytest.raises(ValueError):
        LinkUpdate(
            original_url="https://example.com",
            expires_at=past,
        )

def test_expires_none():
    dt = None

    link = LinkCreate(
        original_url="https://example.com",
        expires_at=dt,
    )
    link2 = LinkUpdate(
        original_url="https://example.com",
        expires_at=dt,
    )
    assert link.expires_at == None
    assert link2.expires_at == None