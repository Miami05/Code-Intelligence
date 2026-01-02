class Database:
    """Database connection manager."""
    
    def __init__(self, url):
        self.url = url
        self.connected = False
    
    def connect(self):
        """Establish connection."""
        self.connected = True
        return True
    
    def disconnect(self):
        """Close connection."""
        self.connected = False
    
    def execute(self, query):
        """Execute query."""
        if not self.connected:
            raise RuntimeError("Not connected")
        return []

def get_connection(url):
    """Factory function for database connection."""
    db = Database(url)
    db.connect()
    return db
