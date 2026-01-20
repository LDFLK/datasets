"""
Shared HTTP client for making async HTTP requests.
Provides a singleton aiohttp ClientSession that can be reused across services.
"""

from aiohttp import ClientSession
import atexit


class HttpClient:
    """Singleton HTTP client that manages a shared aiohttp session."""
    
    def __init__(self):
        self._session: ClientSession = None
    
    @property
    def session(self) -> ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = ClientSession()
            # Register cleanup on exit
            atexit.register(self._cleanup)
        return self._session
    
    def _cleanup(self):
        """Close the session on exit."""
        if self._session and not self._session.closed:
            # Note: This is a synchronous cleanup, but aiohttp sessions
            # should be closed in an async context. For proper cleanup,
            # consider using async context managers in your application.
            pass
    
    async def close(self):
        """Manually close the session (should be called in async context)."""
        if self._session and not self._session.closed:
            await self._session.close()


# Singleton instance
http_client = HttpClient()
