class BaseTracker:
    """Base class for all trackers."""
    def __init__(self, colors=None):
        self.colors = colors if colors is not None else []
    
    def get_colors(self):
        """Returns the colors used for display."""
        return self.colors
    
    def get_activity(self):
        """Fetch activity data. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")