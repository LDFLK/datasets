from aiohttp import ClientSession, ClientTimeout
from typing import Optional

class HTTPClient:
    "Single HTTP client for the application"

    def __init__(self):
        self._session: Optional[ClientSession] = None
        self.timeout = ClientTimeout(total=90, connect=30, sock_connect=30, sock_read=90)

    async def start(self):
        """Create session on app startup"""
        if self._session is None or self._session.closed:
            self._session = ClientSession(timeout=self.timeout)

    async def close(self):
        """Close session on app shutdown"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError("HTTP client not initialized")
        return self._session

# Create a global instance
http_client = HTTPClient()