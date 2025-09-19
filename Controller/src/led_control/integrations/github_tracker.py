"""
GitHubTracker integration module.

Provides the GitHubTracker class for retrieving and
analyzing recent GitHub events for a user.

Features:
- Fetches events with pagination, retry, and rate limit handling
- Counts events per day for a configurable window
"""

import time
import requests


class GitHubTracker:
    """
    Tracks and analyzes recent GitHub events for a user.
    """

    def __init__(self, github_username, api_key):
        if not github_username or not isinstance(github_username, str):
            raise ValueError("github_username must be a non-empty string")
        if not api_key or not isinstance(api_key, str):
            raise ValueError("api_key must be a non-empty string")
        self._auth_info = (github_username, api_key)
        self._num_days = 28
        self._last_event_id = None
        self.max_events = 200
        self._per_page = 30
        self._max_retries = 3
        self._headers = {
            "Authorization": f"Bearer {self._auth_info[1]}",
            "User-Agent": "PiZero",
        }

    def get_username(self):
        """Returns the GitHub username."""
        return self._auth_info[0]

    def _fetch_events(self):
        """
        Fetch recent GitHub events for the configured user,
        handling pagination, retries, and rate limits.
        Returns:
            list: List of GitHub event dicts.
        """
        all_events = []
        page = 1
        while len(all_events) < self.max_events:
            url = f"https://api.github.com/users/{self._auth_info[0]}/events?page={page}&per_page={self._per_page}"
            retries = 0
            while retries < self._max_retries:
                try:
                    print(f"Fetching page {page} (attempt {retries+1})...")
                    response = requests.get(url, headers=self._headers, timeout=10)
                    if response.status_code == 200:
                        events = response.json()
                        all_events.extend(events)
                        if len(events) < self._per_page:
                            return all_events[: self.max_events]
                        break
                    if (
                        response.status_code == 403
                        and "X-RateLimit-Remaining" in response.headers
                        and response.headers["X-RateLimit-Remaining"] == "0"
                    ):
                        reset_time = int(
                            response.headers.get("X-RateLimit-Reset", time.time() + 60)
                        )
                        wait_seconds = max(0, reset_time - int(time.time()))
                        print(f"Rate limit exceeded. Waiting {wait_seconds} seconds...")
                        time.sleep(wait_seconds + 1)
                        retries += 1
                    else:
                        print(
                            f"API Error {response.status_code}: {response.text[:200]}"
                        )
                        retries += 1
                        time.sleep(2**retries)
                except requests.RequestException as exc:
                    print(f"Request failed: {exc}")
                    retries += 1
                    time.sleep(2**retries)
            else:
                print(f"Failed to fetch page {page} after {self._max_retries} retries.")
                break
            page += 1
            time.sleep(1)
        return all_events[: self.max_events]

    def get_event_counts(self):
        """
        Count events per day for the last num_days.
        Returns:
            list: Event counts per day.
        """
        events = self._fetch_events()
        event_counts = [0] * self._num_days
        now = time.time()
        for event in events:
            try:
                created_at = event.get("created_at")
                if not created_at or len(created_at) < 10:
                    continue
                year = int(created_at[0:4])
                month = int(created_at[5:7])
                day = int(created_at[8:10])
                event_time = time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
                seconds_per_day = 24 * 60 * 60
                days_ago = int((now - event_time) // seconds_per_day)
                if 0 <= days_ago < self._num_days:
                    event_counts[days_ago] += 1
            except Exception as exc:
                print(f"Error processing event: {exc}")
        return event_counts
