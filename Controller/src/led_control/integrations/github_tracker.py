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
from led_control.integrations.base_tracker import BaseTracker


class GitHubTracker(BaseTracker):
    """
    Tracks and analyzes recent GitHub events for a user.
    """

    def __init__(self, github_username, api_key, colors=None):
        super().__init__(colors=colors)

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
        self._every_other = True
        self._stored_events = []
        self._seconds_per_day = 86400
        self._headers = {
            "Authorization": f"Bearer {self._auth_info[1]}",
            "User-Agent": "PiZero",
        }

    def _fetch_events(self):
        """
        Fetch recent GitHub events for the configured user,
        handling pagination, retries, and rate limits.
        Returns:
            list: List of GitHub event dicts.
        """
        # Serve cached results every other call to reduce API usage
        if not self._every_other and self._stored_events:
            self._every_other = True
            return self._stored_events

        self._every_other = False
        all_events = []
        page = 1

        while len(all_events) < self.max_events:
            url = f"https://api.github.com/users/{self._auth_info[0]}/events"
            params = {"page": page, "per_page": self._per_page}
            retries = 0
            last_page = False

            while retries < self._max_retries:
                try:
                    resp = requests.get(url, headers=self._headers, params=params, timeout=10)
                    if resp.status_code == 200:
                        events = resp.json() or []
                        all_events.extend(events)
                        last_page = len(events) < self._per_page
                        break

                    # Rate limit handling
                    if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
                        reset_hdr = resp.headers.get("X-RateLimit-Reset")
                        try:
                            reset_time = int(reset_hdr) if reset_hdr else int(time.time()) + 60
                        except ValueError:
                            reset_time = int(time.time()) + 60
                        wait_seconds = max(0, reset_time - int(time.time()))
                        print(f"Rate limit exceeded. Waiting {wait_seconds} seconds...")
                        time.sleep(wait_seconds + 1)
                        retries += 1
                        continue

                    print(f"API Error {resp.status_code}: {resp.text[:200]}")
                    retries += 1
                    time.sleep(2 ** retries)

                except requests.RequestException as exc:
                    print(f"Request failed: {exc}")
                    retries += 1
                    time.sleep(2 ** retries)
            else:
                print(f"Failed to fetch page {page} after {self._max_retries} retries.")
                break

            if last_page:
                break

            page += 1
            time.sleep(1)

        limited = all_events[: self.max_events]
        if limited:
            self._stored_events = limited
            return limited

        return self._stored_events


    def get_activity(self):
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

                year, month, day = int(created_at[0:4]), int(created_at[5:7]), int(created_at[8:10])
                event_time = time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
                days_ago = int((now - event_time) // self._seconds_per_day)

                if 0 <= days_ago < self._num_days:
                    event_counts[days_ago] += 1

            except Exception as exc:
                print(f"Error processing event: {exc}")

        return event_counts
