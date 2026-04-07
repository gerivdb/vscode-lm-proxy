"""
Automatically extracted ProviderConfig class
"""


class ProviderConfig:
    """Configuration for a provider"""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    rate_limit: int = 100  # requests per minute
    retry_attempts: int = 3
    retry_delay: float = 1.0
