import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
import time
import json


class SpotifyTracker:
    """Simple Spotify integration to check if music is currently playing."""
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri or 'http://127.0.0.1:8888/callback'
        self.scope = 'user-read-playback-state user-read-currently-playing'
        self.cache_path = os.path.expanduser("~/.cache/ccal_spotify_token")
        self.sp = None
        
        if self._load_cached_token():
            print("Using cached Spotify token")
        else:
            print("No valid Spotify token found")
    
    def _load_cached_token(self):
        """Load cached token if it exists and is valid."""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r') as f:
                    token_info = json.load(f)
                
                auth_manager = SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=self.redirect_uri,
                    scope=self.scope,
                    cache_path=self.cache_path,
                    open_browser=False
                )
                
                if auth_manager.is_token_expired(token_info):
                    print("Token expired, attempting refresh...")
                    token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
                    
                self.sp = spotipy.Spotify(auth=token_info['access_token'])
                return True
        except Exception as e:
            print(f"Failed to load cached token: {e}")
        return False
    
    def _save_token(self, token_info):
        """Save token to cache file."""
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, 'w') as f:
                json.dump(token_info, f)
        except Exception as e:
            print(f"Failed to save token: {e}")
    
    def setup_authentication(self):
        """
        User-friendly authentication setup for headless devices.
        Returns True if successful, False otherwise.
        """
        if not self.client_id or not self.client_secret:
            print("Spotify client ID and secret are required")
            return False
            
        print("\nSPOTIFY SETUP")
        print("=" * 40)
        print("Setting up Spotify integration for your CCal device...")
        
        try:
            device_code_url = "https://accounts.spotify.com/api/token"
            device_auth_url = "https://accounts.spotify.com/authorize"
            
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=self.cache_path,
                open_browser=False
            )
            
            auth_url = auth_manager.get_authorize_url()
            
            print(f"\nSETUP INSTRUCTIONS:")
            print(f"1. Open this URL in any web browser (phone, computer, etc.):")
            print(f"   {auth_url}")
            print(f"\n2. Sign in to Spotify and authorize the app")
            print(f"3. After authorization, you'll be redirected to a page that won't load")
            print(f"4. Copy the ENTIRE URL from your browser's address bar")
            print(f"5. Paste it below and press Enter")
            
            callback_url = input("\nPaste the full callback URL here: ").strip()
            
            if "code=" not in callback_url:
                print("Invalid URL - missing authorization code")
                return False
            
            code = callback_url.split("code=")[1].split("&")[0]
            
            token_info = auth_manager.get_access_token(code, as_dict=True)
            
            if token_info:
                self._save_token(token_info)
                self.sp = spotipy.Spotify(auth=token_info['access_token'])
                print("Spotify authentication successful!")
                return True
            else:
                print("Failed to get access token")
                return False
                
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def is_playing(self):
        """
        Check if Spotify is currently playing music.
        
        Returns:
            bool: True if music is playing, False otherwise
        """
        if self.sp is None:
            if not self.setup_authentication():
                return False
                
        try:
            current_playback = self.sp.current_playback()
            
            if current_playback is None:
                return False
                
            return current_playback.get('is_playing', False)
        
        except Exception as e:
            print(f"Error checking Spotify playback: {e}")
            if "401" in str(e) or "unauthorized" in str(e).lower():
                print("Authentication expired. Please run setup again.")
                if os.path.exists(self.cache_path):
                    os.remove(self.cache_path)
                self.sp = None
            return False
    
    def is_authenticated(self):
        """Check if we have valid Spotify authentication."""
        return self.sp is not None
