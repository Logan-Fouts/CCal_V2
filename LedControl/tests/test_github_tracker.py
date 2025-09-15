"""Unit tests for the GithubTracker class in CCal_V2."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from github_tracker import GithubTracker
import time
from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture
def mock_config():
    """Fixture for a mock GitHub config dictionary."""
    return {
        "GITHUB_USERNAME": "testuser",
        "GITHUB_TOKEN": "testtoken",
        "LAST_EVENT_ID": "12345",
    }


def make_event(days_ago, event_id="1", event_type="PushEvent", repo_name="repo/test"):
    """Helper to create a mock GitHub event with a given days_ago offset."""
    event_time = time.gmtime(time.time() - days_ago * 86400)
    created_at = time.strftime("%Y-%m-%dT00:00:00Z", event_time)
    return {
        "id": event_id,
        "type": event_type,
        "repo": {"name": repo_name},
        "created_at": created_at,
    }


@patch("github_tracker.ConfigManager")
@patch("github_tracker.requests.get")
def test_fetch_github_events_basic(mock_get, mock_config_manager, mock_config):
    """Test fetching GitHub events across multiple pages and counting per day."""
    # Setup
    mock_config_manager.return_value.load_config.return_value = mock_config
    # Simulate 2 pages of events, 30 each, then less than per_page
    events_page1 = [make_event(0, str(i)) for i in range(30)]
    events_page2 = [make_event(1, str(i + 30)) for i in range(30)]
    events_page3 = [make_event(2, str(i + 60)) for i in range(10)]
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: events_page1),
        MagicMock(status_code=200, json=lambda: events_page2),
        MagicMock(status_code=200, json=lambda: events_page3),
    ]
    tracker = GithubTracker(num_days=3)
    counts = tracker.fetch_github_events(max_events=70)
    # Should count events for 3 days
    assert sum(counts) == 70
    assert counts[0] == 30  # today
    assert counts[1] == 30  # 1 day ago
    assert counts[2] == 10  # 2 days ago


def test_get_event_counts_handles_dates():
    """Test get_event_counts correctly counts events by date and ignores invalid dates."""
    tracker = GithubTracker(num_days=5)
    now = time.time()
    events = [
        {"created_at": time.strftime("%Y-%m-%dT00:00:00Z", time.gmtime(now))},  # today
        {
            "created_at": time.strftime("%Y-%m-%dT00:00:00Z", time.gmtime(now - 86400))
        },  # 1 day ago
        {
            "created_at": time.strftime(
                "%Y-%m-%dT00:00:00Z", time.gmtime(now - 2 * 86400)
            )
        },  # 2 days ago
        {"created_at": "invalid-date"},  # should be ignored
    ]
    counts = tracker.get_event_counts(events)
    assert counts[0] == 1
    assert counts[1] == 1
    assert counts[2] == 1
    assert sum(counts) == 3


@patch("github_tracker.ConfigManager")
@patch("github_tracker.requests.get")
def test_print_new_events_prints_and_updates(
    mock_get, mock_config_manager, mock_config
):
    """Test print_new_events prints new events and updates LAST_EVENT_ID."""
    # Setup
    config = dict(mock_config)
    mock_config_manager.return_value.load_config.return_value = config
    mock_config_manager.return_value.save_config = MagicMock()
    # Simulate 3 events, 2 are new
    events = [
        {
            "id": "999",
            "type": "PushEvent",
            "repo": {"name": "repo1"},
            "created_at": "2025-09-15T00:00:00Z",
        },
        {
            "id": "888",
            "type": "PullRequestEvent",
            "repo": {"name": "repo2"},
            "created_at": "2025-09-14T00:00:00Z",
        },
        {
            "id": "12345",
            "type": "IssuesEvent",
            "repo": {"name": "repo3"},
            "created_at": "2025-09-13T00:00:00Z",
        },
    ]
    mock_get.return_value = MagicMock(status_code=200, json=lambda: events)
    tracker = GithubTracker(num_days=3)
    result = tracker.print_new_events()
    assert result is True
    # LAST_EVENT_ID should be updated
    assert config["LAST_EVENT_ID"] == "999"
    mock_config_manager.return_value.save_config.assert_called_once()


@patch("github_tracker.ConfigManager")
@patch("github_tracker.requests.get")
def test_print_new_events_no_new(mock_get, mock_config_manager, mock_config):
    """Test print_new_events returns False and does not update if no new events."""
    config = dict(mock_config)
    mock_config_manager.return_value.load_config.return_value = config
    mock_config_manager.return_value.save_config = MagicMock()
    # Simulate no new events
    events = [
        {
            "id": "12345",
            "type": "PushEvent",
            "repo": {"name": "repo1"},
            "created_at": "2025-09-15T00:00:00Z",
        },
    ]
    mock_get.return_value = MagicMock(status_code=200, json=lambda: events)
    tracker = GithubTracker(num_days=3)
    result = tracker.print_new_events()
    assert result is False
    mock_config_manager.return_value.save_config.assert_not_called()
