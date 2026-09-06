import pytest
from unittest.mock import patch, MagicMock
from app.storage.incident_repository import IncidentRepository

@pytest.fixture
def repository():
    with patch("app.storage.incident_repository.client") as mock_client:
        mock_client.indices.exists.return_value = True
        repo = IncidentRepository()
        yield repo, mock_client

def test_get_dashboard_summary_empty(repository):
    repo, mock_client = repository
    mock_client.search.return_value = {
        "hits": {"total": {"value": 0}},
        "aggregations": {
            "status": {"buckets": []},
            "risk": {"buckets": []}
        }
    }
    
    summary = repo.get_dashboard_summary()
    assert summary["total_incidents"] == 0
    assert summary["open_incidents"] == 0
    assert summary["investigating_incidents"] == 0
    assert summary["resolved_incidents"] == 0

def test_get_dashboard_summary_open_only(repository):
    repo, mock_client = repository
    mock_client.search.return_value = {
        "hits": {"total": {"value": 1}},
        "aggregations": {
            "status": {"buckets": [{"key": "OPEN", "doc_count": 1}]},
            "risk": {"buckets": []}
        }
    }
    
    summary = repo.get_dashboard_summary()
    assert summary["total_incidents"] == 1
    assert summary["open_incidents"] == 1
    assert summary["investigating_incidents"] == 0
    assert summary["resolved_incidents"] == 0

def test_get_dashboard_summary_investigating_only(repository):
    repo, mock_client = repository
    mock_client.search.return_value = {
        "hits": {"total": {"value": 1}},
        "aggregations": {
            "status": {"buckets": [{"key": "INVESTIGATING", "doc_count": 1}]},
            "risk": {"buckets": []}
        }
    }
    
    summary = repo.get_dashboard_summary()
    assert summary["total_incidents"] == 1
    assert summary["open_incidents"] == 0
    assert summary["investigating_incidents"] == 1
    assert summary["resolved_incidents"] == 0

def test_get_dashboard_summary_resolved_only(repository):
    repo, mock_client = repository
    mock_client.search.return_value = {
        "hits": {"total": {"value": 1}},
        "aggregations": {
            "status": {"buckets": [{"key": "RESOLVED", "doc_count": 1}]},
            "risk": {"buckets": []}
        }
    }
    
    summary = repo.get_dashboard_summary()
    assert summary["total_incidents"] == 1
    assert summary["open_incidents"] == 0
    assert summary["investigating_incidents"] == 0
    assert summary["resolved_incidents"] == 1

def test_get_dashboard_summary_mixed(repository):
    repo, mock_client = repository
    mock_client.search.return_value = {
        "hits": {"total": {"value": 15}},
        "aggregations": {
            "status": {"buckets": [
                {"key": "OPEN", "doc_count": 10},
                {"key": "INVESTIGATING", "doc_count": 3},
                {"key": "RESOLVED", "doc_count": 2}
            ]},
            "risk": {"buckets": []}
        }
    }
    
    summary = repo.get_dashboard_summary()
    assert summary["total_incidents"] == 15
    assert summary["open_incidents"] == 10
    assert summary["investigating_incidents"] == 3
    assert summary["resolved_incidents"] == 2
    assert summary["open_incidents"] + summary["investigating_incidents"] + summary["resolved_incidents"] == summary["total_incidents"]
