"""
Base Provider Interface
Abstract base class for LLM provider integrations
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    """Standardized response from any provider"""

    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProviderConfig:
    """Configuration for a provider"""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    rate_limit: int = 100  # requests per minute
    retry_attempts: int = 3
    retry_delay: float = 1.0


class BaseProvider(ABC):
    """
    Abstract base class for LLM provider integrations
    """

    def __init__(self, config: ProviderConfig):
        super().__init__()
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider connection"""
        pass

    @abstractmethod
    async def close(self):
        """Close provider connections"""
        pass

    @abstractmethod
    async def query(
        self, model: str, prompt: str, **kwargs
    ) -> Optional[ProviderResponse]:
        """
        Execute a query against the provider

        Args:
            model: Model name to use
            prompt: Query prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Provider response or None if failed
        """
        pass

    @abstractmethod
    async def batch_query(
        self, model: str, prompts: List[str], **kwargs
    ) -> List[Optional[ProviderResponse]]:
        """
        Execute multiple queries in batch

        Args:
            model: Model name to use
            prompts: List of query prompts
            **kwargs: Additional parameters

        Returns:
            List of provider responses
        """
        pass

    @abstractmethod
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from this provider

        Returns:
            List of model metadata dictionaries
        """
        pass

    @abstractmethod
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific model

        Args:
            model_name: Name of the model

        Returns:
            Model metadata or None if not found
        """
        pass

    @abstractmethod
    async def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check current rate limit status

        Returns:
            Rate limit information
        """
        pass

    async def validate_config(self) -> bool:
        """Validate provider configuration"""
        if self.config.api_key is None:
            logger.warning(f"No API key configured for {self.__class__.__name__}")
            return False
        return True

    async def _handle_rate_limit(self, response_headers: Dict[str, Any]) -> float:
        """
        Handle rate limiting based on response headers

        Returns:
            Delay time in seconds before next request
        """
        # Default implementation - override in subclasses
        return 0.0

    async def _retry_with_backoff(
        self, operation, max_attempts: int = 3, base_delay: float = 1.0
    ):
        """
        Retry operation with exponential backoff

        Args:
            operation: Async function to retry
            max_attempts: Maximum number of attempts
            base_delay: Base delay between attempts

        Returns:
            Operation result or raises last exception
        """
        last_exception = None

        for attempt in range(max_attempts):
            try:
                return await operation()
            except Exception as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {max_attempts} attempts failed: {e}")

        raise last_exception
