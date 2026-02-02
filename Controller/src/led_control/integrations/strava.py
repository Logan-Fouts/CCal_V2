"""
Strava integration module for tracking fitness activities.

Provides the StravaTracker class for retrieving and analyzing 
recent Strava activities for a user.
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta
from led_control.integrations.base_tracker import BaseTracker

class StravaTracker(BaseTracker):
    """Tracks and analyzes recent Strava activities for a user."""
    
    def __init__(self, client_id=None, client_secret=None, num_days=28, colors=None):
        super().__init__(colors=colors)
        self.client_id = client_id
        self.client_secret = client_secret
        self.cache_path = os.path.expanduser("~/.cache/ccal_strava_token")
        self.num_days = num_days
        self.access_token = None
        self.refresh_token = None
        
        self.auth_url = "https://www.strava.com/oauth/authorize"
        self.token_url = "https://www.strava.com/oauth/token"
        self.activities_url = "https://www.strava.com/api/v3/athlete/activities"
        
        if self._load_cached_token():
            pass
        else:
            self.setup_authentication()
    
    def _load_cached_token(self):
        """Load cached token if it exists and is valid."""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r') as f:
                    token_data = json.load(f)
                
                expires_at = token_data.get('expires_at', 0)
                if time.time() < expires_at:
                    self.access_token = token_data['access_token']
                    self.refresh_token = token_data['refresh_token']
                    return True
                else:
                    if self._refresh_access_token(token_data['refresh_token']):
                        return True
        except Exception as e:
            print(f"Failed to load cached token: {e}")
        return False
    
    def _save_token(self, token_data):
        """Save token to cache file."""
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, 'w') as f:
                json.dump(token_data, f)
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
        except Exception as e:
            print(f"Failed to save token: {e}")
    
    def _refresh_access_token(self, refresh_token):
        """Refresh the access token using refresh token."""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(self.token_url, data=data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                self._save_token(token_data)
                return True
            else:
                print(f"Failed to refresh token: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def setup_authentication(self):
        """
        User-friendly authentication setup for Strava integration.
        Returns True if successful, False otherwise.
        """
        if not self.client_id or not self.client_secret:
            print("Strava client ID and secret are required")
            return False
        
        print("\nSTRAVA SETUP")
        print("=" * 40)
        print("Setting up Strava integration for your CCal device...")
        
        try:
            scope = "read,activity:read"
            auth_params = {
                'client_id': self.client_id,
                'redirect_uri': 'http://localhost',
                'response_type': 'code',
                'scope': scope,
                'approval_prompt': 'force'
            }
            
            auth_url = f"{self.auth_url}?" + "&".join([f"{k}={v}" for k, v in auth_params.items()])
            
            print(f"\nSETUP INSTRUCTIONS:")
            print(f"1. Open this URL in any web browser (phone, computer, etc.):")
            print(f"   {auth_url}")
            print(f"\n2. Sign in to Strava and authorize the app")
            print(f"3. After authorization, you'll be redirected to a page that won't load")
            print(f"4. Copy the ENTIRE URL from your browser's address bar")
            print(f"5. Paste it below and press Enter")
            
            callback_url = input("\nPaste the full callback URL here: ").strip()
            
            if "code=" not in callback_url:
                print("Invalid URL - missing authorization code")
                return False
            
            code = callback_url.split("code=")[1].split("&")[0]
            
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(self.token_url, data=token_data, timeout=10)
            
            if response.status_code == 200:
                token_response = response.json()
                self._save_token(token_response)
                print("Strava authentication successful!")
                return True
            else:
                print(f"Failed to exchange code for token: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _fetch_activities(self):
        """
        Fetch recent Strava activities with pagination and rate limiting.
        Returns list of activity dictionaries.
        """
        if not self.access_token:
            if not self.setup_authentication():
                return []
        
        activities = []
        page = 1
        per_page = 50
        max_activities = 200
        
        after = int((datetime.now() - timedelta(days=self.num_days)).timestamp())
        
        while len(activities) < max_activities:
            try:
                headers = {'Authorization': f'Bearer {self.access_token}'}
                params = {
                    'page': page,
                    'per_page': per_page,
                    'after': after
                }
                
                response = requests.get(
                    self.activities_url, 
                    headers=headers, 
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    page_activities = response.json()
                    if not page_activities: 
                        break
                    activities.extend(page_activities)
                    page += 1
                    time.sleep(0.5)
                    
                elif response.status_code == 401:
                    if self.refresh_token and self._refresh_access_token(self.refresh_token):
                        continue 
                    else:
                        print("Authentication expired. Please run setup again.")
                        break
                        
                elif response.status_code == 429:
                    print("Rate limited, waiting...")
                    time.sleep(60)
                    continue
                    
                else:
                    print(f"API Error {response.status_code}: {response.text[:200]}")
                    break
                    
            except requests.RequestException as e:
                print(f"Request failed: {e}")
                break
        
        return activities[:max_activities]
    
    def get_activity(self):
        """
        Count activities per day for the last num_days.
        Returns list of activity counts per day (0 = today, 1 = yesterday, etc.)
        """
        activities = self._fetch_activities()
        activity_counts = [0] * self.num_days
        
        now = datetime.now()
        
        for activity in activities:
            try:
                start_date = activity.get('start_date_local', activity.get('start_date', ''))
                if not start_date:
                    continue
                
                activity_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                
                days_ago = (now.date() - activity_date.date()).days
                
                if 0 <= days_ago < self.num_days:
                    activity_counts[days_ago] += 1
                    
            except Exception as e:
                print(f"Error processing activity: {e}")
                continue
        
        return activity_counts
    
    def is_authenticated(self):
        """Check if we have valid Strava authentication."""
        return self.access_token is not None
    
    def get_recent_activity_summary(self):
        """Get a summary of recent activities for debugging."""
        activities = self._fetch_activities()
        if not activities:
            return "No recent activities found"
        
        activity_types = {}
        for activity in activities[:50]:
            activity_type = activity.get('type', 'Unknown')
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        summary = f"Last {len(activities)} activities: "
        summary += ", ".join([f"{count} {type_}" for type_, count in activity_types.items()])
        return summary
