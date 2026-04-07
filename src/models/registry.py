"""
Model Registry
Manages available LLM models, their metadata, and dynamic registration
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModelMetadata:
    """Metadata for an LLM model"""

    name: str
    provider: str
    context_size: int
    capabilities: List[str] = field(default_factory=list)
    latency_ms: Optional[float] = None
    tokens_per_sec: Optional[float] = None
    cost_per_token: Optional[float] = None
    api_endpoint: Optional[str] = None
    api_key_required: bool = True
    max_tokens_per_request: Optional[int] = None
    supported_parameters: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"  # active, inactive, deprecated


class ModelRegistry:
    """
    Registry for managing LLM models and their metadata
    Supports dynamic registration and discovery
    """

    def __init__(self, config_file: str = "config/models.json"):
        super().__init__()
        self.config_file = config_file
        self.models: Dict[str, ModelMetadata] = {}
        self.providers: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize the model registry"""
        if self._initialized:
            return

        logger.info("Initializing Model Registry...")

        try:
            # Load default models
            await self._load_default_models()

            # Load custom configuration if exists
            await self._load_config()

            # Initialize providers
            await self._initialize_providers()

            self._initialized = True
            logger.info(f"Model Registry initialized with {len(self.models)} models")

        except Exception as e:
            logger.error(f"Failed to initialize model registry: {e}")
            raise

    async def close(self):
        """Cleanup resources"""
        logger.info("Closing Model Registry...")
        # Save current state
        await self._save_config()

    async def get_available_models(self) -> List[ModelMetadata]:
        """Get list of all available models"""
        return list(self.models.values())

    async def get_model(self, model_name: str) -> Optional[ModelMetadata]:
        """Get metadata for a specific model"""
        return self.models.get(model_name)

    async def register_model(self, model_data: Dict[str, Any]) -> bool:
        """Register a new model dynamically"""
        try:
            # Validate required fields
            required_fields = ["name", "provider", "context_size"]
            for field in required_fields:
                if field not in model_data:
                    logger.error(f"Missing required field: {field}")
                    return False

            # Create model metadata
            model = ModelMetadata(
                name=model_data["name"],
                provider=model_data["provider"],
                context_size=model_data["context_size"],
                capabilities=model_data.get("capabilities", []),
                latency_ms=model_data.get("latency_ms"),
                tokens_per_sec=model_data.get("tokens_per_sec"),
                cost_per_token=model_data.get("cost_per_token"),
                api_endpoint=model_data.get("api_endpoint"),
                api_key_required=model_data.get("api_key_required", True),
                max_tokens_per_request=model_data.get("max_tokens_per_request"),
                supported_parameters=model_data.get("supported_parameters", []),
                status=model_data.get("status", "active"),
            )

            # Register model
            self.models[model.name] = model
            logger.info(f"Registered model: {model.name} ({model.provider})")

            # Save configuration
            await self._save_config()

            return True

        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return False

    async def unregister_model(self, model_name: str) -> bool:
        """Remove a model from the registry"""
        if model_name in self.models:
            del self.models[model_name]
            logger.info(f"Unregistered model: {model_name}")
            await self._save_config()
            return True
        return False

    async def update_model_metadata(
        self, model_name: str, updates: Dict[str, Any]
    ) -> bool:
        """Update metadata for an existing model"""
        if model_name not in self.models:
            return False

        model = self.models[model_name]

        # Update allowed fields
        updatable_fields = [
            "capabilities",
            "latency_ms",
            "tokens_per_sec",
            "cost_per_token",
            "api_endpoint",
            "api_key_required",
            "max_tokens_per_request",
            "supported_parameters",
            "status",
        ]

        for field, value in updates.items():
            if field in updatable_fields:
                setattr(model, field, value)

        model.last_updated = datetime.utcnow()

        await self._save_config()
        logger.info(f"Updated metadata for model: {model_name}")
        return True

    async def get_models_by_provider(self, provider: str) -> List[ModelMetadata]:
        """Get all models from a specific provider"""
        return [model for model in self.models.values() if model.provider == provider]

    async def get_models_by_capability(self, capability: str) -> List[ModelMetadata]:
        """Get all models that support a specific capability"""
        return [
            model for model in self.models.values() if capability in model.capabilities
        ]

    async def get_models_for_task(
        self, task_type: str, context_size: int = 4096
    ) -> List[ModelMetadata]:
        """Get models suitable for a specific task type"""
        suitable_models = []

        # Task-specific capability mapping
        task_capabilities = {
            "code_analysis": ["code_analysis", "reasoning"],
            "code_generation": ["code_generation", "coding"],
            "debugging": ["debugging", "reasoning", "code_analysis"],
            "testing": ["testing", "code_generation"],
            "documentation": ["documentation", "writing"],
            "refactoring": ["refactoring", "code_generation"],
            "optimization": ["optimization", "reasoning"],
            "translation": ["translation", "language"],
            "general": [],  # Any model can handle general tasks
        }

        required_capabilities = task_capabilities.get(task_type, [])

        for model in self.models.values():
            # Check if model is active
            if model.status != "active":
                continue

            # Check context size requirement
            if model.context_size < context_size:
                continue

            # Check capabilities (if specific capabilities required)
            if required_capabilities and not any(
                cap in model.capabilities for cap in required_capabilities
            ):
                continue

            suitable_models.append(model)

        return suitable_models

    async def update_config(self, config: Dict[str, Any]) -> bool:
        """Update registry configuration"""
        try:
            # Handle model updates
            if "models" in config:
                for model_data in config["models"]:
                    if "name" in model_data:
                        await self.register_model(model_data)

            # Handle provider updates
            if "providers" in config:
                self.providers.update(config["providers"])

            await self._save_config()
            return True

        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False

    async def _load_default_models(self):
        """Load default model configurations"""
        default_models = [
            # Anthropic Claude models
            {
                "name": "claude-3-5-sonnet-20241022",
                "provider": "anthropic",
                "context_size": 200000,
                "capabilities": [
                    "code_analysis",
                    "code_generation",
                    "debugging",
                    "reasoning",
                    "writing",
                ],
                "latency_ms": 2500,
                "tokens_per_sec": 80,
                "cost_per_token": 0.000015,
                "max_tokens_per_request": 4096,
                "supported_parameters": ["temperature", "max_tokens", "top_p"],
            },
            {
                "name": "claude-3-opus-20240229",
                "provider": "anthropic",
                "context_size": 200000,
                "capabilities": [
                    "code_analysis",
                    "code_generation",
                    "debugging",
                    "reasoning",
                    "writing",
                    "research",
                ],
                "latency_ms": 3000,
                "tokens_per_sec": 70,
                "cost_per_token": 0.000075,
                "max_tokens_per_request": 4096,
                "supported_parameters": ["temperature", "max_tokens", "top_p"],
            },
            # OpenAI GPT models
            {
                "name": "gpt-4",
                "provider": "openai",
                "context_size": 8192,
                "capabilities": [
                    "code_analysis",
                    "code_generation",
                    "debugging",
                    "reasoning",
                    "writing",
                ],
                "latency_ms": 2800,
                "tokens_per_sec": 60,
                "cost_per_token": 0.00006,
                "max_tokens_per_request": 4096,
                "supported_parameters": [
                    "temperature",
                    "max_tokens",
                    "top_p",
                    "frequency_penalty",
                ],
            },
            {
                "name": "gpt-3.5-turbo",
                "provider": "openai",
                "context_size": 16384,
                "capabilities": ["code_generation", "writing", "reasoning"],
                "latency_ms": 1200,
                "tokens_per_sec": 120,
                "cost_per_token": 0.000002,
                "max_tokens_per_request": 4096,
                "supported_parameters": [
                    "temperature",
                    "max_tokens",
                    "top_p",
                    "frequency_penalty",
                ],
            },
            # xAI Grok models
            {
                "name": "grok-beta",
                "provider": "xai",
                "context_size": 128000,
                "capabilities": ["reasoning", "code_analysis", "writing", "research"],
                "latency_ms": 2200,
                "tokens_per_sec": 90,
                "cost_per_token": 0.00001,
                "max_tokens_per_request": 4096,
                "supported_parameters": ["temperature", "max_tokens", "top_p"],
            },
            # Meta Llama models
            {
                "name": "llama-3.2-70b",
                "provider": "meta",
                "context_size": 128000,
                "capabilities": ["code_generation", "reasoning", "translation"],
                "latency_ms": 1800,
                "tokens_per_sec": 100,
                "cost_per_token": 0.000001,
                "max_tokens_per_request": 4096,
                "supported_parameters": ["temperature", "max_tokens", "top_p"],
            },
            # Google Gemini
            {
                "name": "gemini-pro",
                "provider": "google",
                "context_size": 32768,
                "capabilities": ["code_generation", "reasoning", "writing"],
                "latency_ms": 1600,
                "tokens_per_sec": 110,
                "cost_per_token": 0.000005,
                "max_tokens_per_request": 8192,
                "supported_parameters": ["temperature", "max_tokens", "top_p"],
            },
            # Mistral AI
            {
                "name": "mistral-7b-instruct",
                "provider": "mistral",
                "context_size": 32768,
                "capabilities": ["code_generation", "writing", "translation"],
                "latency_ms": 1000,
                "tokens_per_sec": 150,
                "cost_per_token": 0.0000005,
                "max_tokens_per_request": 4096,
                "supported_parameters": ["temperature", "max_tokens", "top_p"],
            },
            # Alibaba Qwen
            {
                "name": "qwen-2.5-72b",
                "provider": "alibaba",
                "context_size": 32768,
                "capabilities": [
                    "code_analysis",
                    "code_generation",
                    "debugging",
                    "reasoning",
                ],
                "latency_ms": 2000,
                "tokens_per_sec": 85,
                "cost_per_token": 0.000002,
                "max_tokens_per_request": 4096,
                "supported_parameters": ["temperature", "max_tokens", "top_p"],
            },
        ]

        for model_data in default_models:
            await self.register_model(model_data)

    async def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                # Load custom models
                if "models" in config:
                    for model_data in config["models"]:
                        await self.register_model(model_data)

                # Load provider configurations
                if "providers" in config:
                    self.providers.update(config["providers"])

                logger.info(f"Loaded configuration from {self.config_file}")

            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")

    async def _save_config(self):
        """Save current configuration to file"""
        try:
            config = {
                "models": [
                    {
                        "name": model.name,
                        "provider": model.provider,
                        "context_size": model.context_size,
                        "capabilities": model.capabilities,
                        "latency_ms": model.latency_ms,
                        "tokens_per_sec": model.tokens_per_sec,
                        "cost_per_token": model.cost_per_token,
                        "api_endpoint": model.api_endpoint,
                        "api_key_required": model.api_key_required,
                        "max_tokens_per_request": model.max_tokens_per_request,
                        "supported_parameters": model.supported_parameters,
                        "status": model.status,
                    }
                    for model in self.models.values()
                    if model.name
                    not in [
                        "claude-3-5-sonnet-20241022",
                        "claude-3-opus-20240229",
                        "gpt-4",
                        "gpt-3.5-turbo",
                        "grok-beta",
                        "llama-3.2-70b",
                        "gemini-pro",
                        "mistral-7b-instruct",
                        "qwen-2.5-72b",
                    ]  # Don't save defaults
                ],
                "providers": self.providers,
            }

            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    async def _initialize_providers(self):
        """Initialize provider configurations"""
        # Default provider configurations
        default_providers = {
            "anthropic": {
                "base_url": "https://api.anthropic.com",
                "api_version": "2023-06-01",
                "rate_limit": 50,  # requests per minute
                "timeout": 60,
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "rate_limit": 100,
                "timeout": 60,
            },
            "xai": {"base_url": "https://api.x.ai/v1", "rate_limit": 30, "timeout": 60},
            "meta": {
                "base_url": "https://api.meta.ai",
                "rate_limit": 20,
                "timeout": 60,
            },
            "google": {
                "base_url": "https://generativelanguage.googleapis.com",
                "rate_limit": 60,
                "timeout": 60,
            },
            "mistral": {
                "base_url": "https://api.mistral.ai/v1",
                "rate_limit": 30,
                "timeout": 60,
            },
            "alibaba": {
                "base_url": "https://api.alibabacloud.com",
                "rate_limit": 25,
                "timeout": 60,
            },
        }

        # Merge with existing providers
        for provider, config in default_providers.items():
            if provider not in self.providers:
                self.providers[provider] = config

    async def get_provider_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific provider"""
        return self.providers.get(provider)

    async def update_provider_config(
        self, provider: str, config: Dict[str, Any]
    ) -> bool:
        """Update configuration for a provider"""
        try:
            if provider not in self.providers:
                self.providers[provider] = {}

            self.providers[provider].update(config)
            await self._save_config()
            return True

        except Exception as e:
            logger.error(f"Failed to update provider config: {e}")
            return False
