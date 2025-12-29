import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyTracker:
    """Simple Spotify integration to check if music is currently playing."""
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        """Initialize the Spotify tracker with credentials."""
        # Default credentials (consider moving to config)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri or 'http://127.0.0.1:8888/callback'
        
        # Required scopes for playback info
        self.scope = 'user-read-playback-state user-read-currently-playing'
        
        # Initialize Spotify client
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        ))
    
    def is_playing(self):
        """
        Check if Spotify is currently playing music.
        
        Returns:
            bool: True if music is playing, False otherwise
        """
        try:
            current_playback = self.sp.current_playback()
            
            if current_playback is None:
                return False
            
            return current_playback.get('is_playing', False)
        
        except Exception as e:
            # Handle any API errors gracefully
            print(f"Error checking Spotify playback: {e}")
            return False


# Example usage (can be removed in production)
if __name__ == "__main__":
    tracker = SpotifyTracker()
    
    if tracker.is_playing():
        print("🎵 Music is currently playing!")
    else:
        print("🔇 No music playing.")