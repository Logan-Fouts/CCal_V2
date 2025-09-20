"""
Unit tests for the GitHubTracker integration module.

This test suite covers:
- Initialization and argument validation
- Event fetching (success, pagination, API errors, rate limiting, network errors)
- Event counting (normal, malformed, and empty event lists)

Mocks are used to simulate API responses and error conditions.
"""

import time
from unittest.mock import Mock, patch
import requests
from led_control.integrations.github_tracker import GitHubTracker

API_KEY = "blahblah"
NUM_DAYS = 28
GITHUB_USERNAME = "Logan-Fouts"
RESPONSE_JSON = [
    {
        "id": "22249084947",
        "type": "WatchEvent",
        "actor": {"id": 583231, "login": "octocat"},
        "repo": {"id": 1296269, "name": "octocat/Hello-World"},
        "payload": {"action": "started"},
        "public": True,
        "created_at": "2022-06-09T12:47:28Z",
    },
    {
        "id": "22249084964",
        "type": "PushEvent",
        "actor": {"id": 583231, "login": "octocat"},
        "repo": {"id": 1296269, "name": "octocat/Hello-World"},
        "payload": {"push_id": 10115855396},
        "public": False,
        "created_at": "2022-06-07T07:50:26Z",
    },
]


def test_github_tracker_initialization():
    """Test initializing GitHubTracker with arguments."""
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    assert gt._auth_info == (GITHUB_USERNAME, API_KEY)
    assert gt._num_days == NUM_DAYS
    assert gt._last_event_id is None
    assert gt.max_events == 200
    assert gt._per_page == 30
    assert gt._max_retries == 3


@patch("led_control.integrations.github_tracker.requests.get")
def test_fetch_events_success(mock_get):
    """Test that _fetch_events retrieves and processes events correctly."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = RESPONSE_JSON
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    events = gt._fetch_events()
    assert isinstance(events, list)
    assert len(events) == 2
    assert events[0]["id"] == "22249084947"
    assert events[1]["id"] == "22249084964"


@patch("led_control.integrations.github_tracker.requests.get")
def test_fetch_events_pagination(mock_get):
    """Test that _fetch_events handles pagination correctly."""
    first_page = RESPONSE_JSON * 15  # 30 events
    second_page = RESPONSE_JSON[:1]  # 1 event
    mock_get.side_effect = [
        Mock(status_code=200, json=Mock(return_value=first_page)),
        Mock(status_code=200, json=Mock(return_value=second_page)),
    ]
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    gt.max_events = 31
    events = gt._fetch_events()
    assert len(events) == 31


@patch("led_control.integrations.github_tracker.requests.get")
def test_fetch_events_api_error(mock_get):
    """Test that _fetch_events handles API errors gracefully."""
    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Internal Server Error"
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    events = gt._fetch_events()
    assert events == []


@patch("led_control.integrations.github_tracker.requests.get")
def test_fetch_events_rate_limit(mock_get):
    """Test that _fetch_events handles rate limiting correctly."""
    rate_limit_resp = Mock(
        status_code=403,
        headers={
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 1),
        },
        text="Rate limit exceeded",
    )
    success_resp = Mock(status_code=200, json=Mock(return_value=RESPONSE_JSON))
    mock_get.side_effect = [rate_limit_resp, success_resp]
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    events = gt._fetch_events()
    assert len(events) == 2


@patch("led_control.integrations.github_tracker.requests.get")
def test_fetch_events_retries_on_network_error(mock_get):
    """Test that _fetch_events retries on network errors."""
    mock_get.side_effect = [
        requests.RequestException("fail"),
        Mock(status_code=200, json=Mock(return_value=RESPONSE_JSON)),
    ]
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    events = gt._fetch_events()
    assert len(events) == 2


@patch("led_control.integrations.github_tracker.requests.get")
def test_get_event_counts_normal(mock_get):
    """Test that get_event_counts returns correct counts."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = RESPONSE_JSON
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    counts = gt.get_event_counts()
    assert isinstance(counts, list)
    assert len(counts) == NUM_DAYS


@patch("led_control.integrations.github_tracker.requests.get")
def test_get_event_counts_malformed_event(mock_get):
    """Test that get_event_counts handles malformed events."""
    malformed = [{"id": "bad"}] + RESPONSE_JSON
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = malformed
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    counts = gt.get_event_counts()
    assert isinstance(counts, list)
    assert len(counts) == NUM_DAYS


@patch("led_control.integrations.github_tracker.requests.get")
def test_get_event_counts_empty(mock_get):
    """Test that get_event_counts handles empty event lists."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = []
    gt = GitHubTracker(GITHUB_USERNAME, API_KEY)
    counts = gt.get_event_counts()
    assert counts == [0] * NUM_DAYS
