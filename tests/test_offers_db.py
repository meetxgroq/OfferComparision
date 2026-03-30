"""Tests for utils/offers_db.py CRUD operations."""
import pytest
from unittest.mock import MagicMock, patch

SAMPLE_OFFER = {
    "client_id": "1711700000000",
    "company": "Acme Corp",
    "position": "Senior Engineer",
    "location": "San Francisco, CA",
    "base_salary": 200000,
    "equity": 50000,
    "bonus": 20000,
    "currency": "USD",
}


@patch("utils.offers_db._get_supabase")
def test_list_offers_returns_list(mock_sb):
    from utils.offers_db import list_offers
    mock_sb.return_value.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [SAMPLE_OFFER]
    result = list_offers("user-uuid-123")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["company"] == "Acme Corp"


@patch("utils.offers_db._get_supabase")
def test_upsert_offers_calls_upsert(mock_sb):
    from utils.offers_db import upsert_offers
    mock_sb.return_value.table.return_value.upsert.return_value.execute.return_value.data = [SAMPLE_OFFER]
    result = upsert_offers("user-uuid-123", [SAMPLE_OFFER])
    assert isinstance(result, list)
    mock_sb.return_value.table.return_value.upsert.assert_called_once()


@patch("utils.offers_db._get_supabase")
def test_delete_offer_by_id(mock_sb):
    from utils.offers_db import delete_offer
    mock_sb.return_value.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()
    delete_offer("user-uuid-123", "some-uuid")
    mock_sb.return_value.table.return_value.delete.assert_called_once()


@patch("utils.offers_db._get_supabase")
def test_delete_offer_by_client_id(mock_sb):
    from utils.offers_db import delete_offer_by_client_id
    mock_sb.return_value.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()
    delete_offer_by_client_id("user-uuid-123", "1711700000000")
    mock_sb.return_value.table.return_value.delete.assert_called_once()


@patch("utils.offers_db._get_supabase")
def test_upsert_filters_to_known_columns(mock_sb):
    from utils.offers_db import upsert_offers
    offer_with_extras = {**SAMPLE_OFFER, "unknown_field": "should_be_dropped"}
    mock_sb.return_value.table.return_value.upsert.return_value.execute.return_value.data = [SAMPLE_OFFER]
    upsert_offers("user-uuid-123", [offer_with_extras])
    call_args = mock_sb.return_value.table.return_value.upsert.call_args[0][0]
    assert "unknown_field" not in call_args[0]
