"""
Automatically extracted HTTPConnectionPool class
"""


class HTTPConnectionPool:
    """Optimized HTTP connection pool for external API calls"""

    def __init__(self, max_connections: int = 100, timeout: int = 30):
        super().__init__()
        self.max_connections = max_connections
        self.timeout = ClientTimeout(total=timeout)
        self._session: Optional[ClientSession] = None
        self._lock = asyncio.Lock()

    async def get_session(self) -> ClientSession:
        """Get or create optimized HTTP session"""
        async with self._lock:
            if self._session is None or self._session.closed:
                connector = TCPConnector(
                    limit=self.max_connections,
                    limit_per_host=10,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    keepalive_timeout=60,
                    enable_cleanup_closed=True,
                )
                self._session = ClientSession(
                    connector=connector, timeout=self.timeout, trust_env=True
                )
            return self._session

    async def close(self):
        """Close HTTP session"""
        async with self._lock:
            if self._session and not self._session.closed:
                await self._session.close()
