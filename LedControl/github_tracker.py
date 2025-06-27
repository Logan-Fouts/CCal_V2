import requests
import time
from config_manager import CONFIG_MANAGER

class GITHUB_TRACKER:
    def __init__(self, num_days):
        self.num_days = num_days
        self.config_manager = CONFIG_MANAGER()
        
    def fetch_github_events(self, max_events=100):
        config = self.config_manager.load_config()
        all_events = []
        page = 1
        per_page = 30
        
        while len(all_events) < max_events:
            url = f"https://api.github.com/users/{config['GITHUB_USERNAME']}/events?page={page}&per_page={per_page}"
            headers = {
                "Authorization": f"Bearer {config['GITHUB_TOKEN']}",
                "User-Agent": "PiZero"
            }
            
            try:
                print(f"Fetching page {page}...")
                response = requests.get(url, headers=headers)
                
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
                
            except Exception as e:
                print(f"Request failed: {str(e)}")
                break
                
        print(f"Total events collected: {len(all_events)}")
        return self.get_event_counts(all_events[:max_events])

    def get_event_counts(self, events):
        event_counts = [0] * self.num_days
        now = time.time()
        
        for event in events:
            try:
                created_at = event['created_at']
                year = int(created_at[0:4])
                month = int(created_at[5:7])
                day = int(created_at[8:10])
                
                event_time = time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
                days_ago = int((now - event_time) // 86400)
                
                if 0 <= days_ago < self.num_days:
                    event_counts[days_ago] += 1
                    
            except Exception as e:
                print(f"Error processing event: {str(e)}")
        
        print("Event counts:", event_counts)
        return event_counts

