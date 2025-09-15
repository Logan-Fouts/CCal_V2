"""GitHub event tracker for CCal_V2."""

import time
import requests
from config_manager import ConfigManager


class GithubTracker:
    """Tracks GitHub events for a user."""

    def __init__(self, num_days, config_file):
        """Initialize the tracker."""
        self.num_days = num_days
        self.config_manager = ConfigManager(config_file)

    def fetch_github_events(self, max_events=200):
        """
        Fetch recent GitHub events for the configured user.

        Args:
            max_events (int): Maximum number of events to fetch.

        Returns:
            list: Event counts per day.
        """
        config = self.config_manager.load_config()
        all_events = []
        page = 1
        per_page = 30

        while len(all_events) < max_events:
            url = (
                f"https://api.github.com/users/{config['GITHUB_USERNAME']}/events"
                f"?page={page}&per_page={per_page}"
            )
            headers = {
                "Authorization": f"Bearer {config['GITHUB_TOKEN']}",
                "User-Agent": "PiZero",
            }

            try:
                print(f"Fetching page {page}...")
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code != 200:
                    print(f"API Error {response.status_code}: {response.text[:200]}")
                    break

                events = response.json()
                print(f"Got {len(events)} events in page {page}")
                all_events.extend(events)

                if len(events) < per_page:
                    break

                page += 1
                time.sleep(1)

            except requests.RequestException as exc:
                print(f"Request failed: {exc}")
                break

        print(f"Total events collected: {len(all_events)}")
        return self.get_event_counts(all_events[:max_events])

    def get_event_counts(self, events):
        """
        Count events per day for the last num_days.

        Args:
            events (list): List of GitHub event dicts.

        Returns:
            list: Event counts per day.
        """
        event_counts = [0] * self.num_days
        now = time.time()

        for event in events:
            try:
                created_at = event["created_at"]
                year = int(created_at[0:4])
                month = int(created_at[5:7])
                day = int(created_at[8:10])

                event_time = time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
                days_ago = int((now - event_time) // 86400)

                if 0 <= days_ago < self.num_days:
                    event_counts[days_ago] += 1

            except Exception as exc:
                print(f"Error processing event: {exc}")

        print("Event counts:", event_counts)
        return event_counts

    def print_new_events(self):
        """
        Print new GitHub events since the last seen event.

        Returns:
            bool: True if new events were found, False otherwise.
        """
        config = self.config_manager.load_config()
        last_event_id = config.get("LAST_EVENT_ID")
        url = f"https://api.github.com/users/{config['GITHUB_USERNAME']}/events?per_page=10"
        headers = {
            "Authorization": f"Bearer {config['GITHUB_TOKEN']}",
            "User-Agent": "PiZero",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"API Error {response.status_code}: {response.text[:200]}")
                return False
            events = response.json()
            new_events = []
            for event in events:
                if event["id"] == last_event_id:
                    break
                new_events.append(event)
            if new_events:
                print(f"New GitHub events ({len(new_events)}):")
                for event in reversed(new_events):
                    print(
                        f"- [{event['type']}] {event.get('repo', {}).get('name', '')} at {event['created_at']}"
                    )
                # Update last seen event ID
                config["LAST_EVENT_ID"] = events[0]["id"]
                self.config_manager.save_config(config)
                return True
            print("No new GitHub events.")
            return False
        except requests.RequestException as exc:
            print(f"Failed to fetch events: {exc}")
            return False
