"""
Basic tests for LM Hack Proxy
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.registry import ModelRegistry
from models.router import TaskRouter
from utils.monitoring.metrics import MetricsCollector

from agents.coordinator import AgentCoordinator


class TestModelRegistry:
    """Test Model Registry functionality"""

    @pytest.mark.asyncio
    async def test_registry_initialization(self):
        """Test that registry initializes correctly"""
        registry = ModelRegistry()

        # Mock the file operations to avoid file system dependencies
        with patch.object(registry, "_load_default_models"), patch.object(
            registry, "_load_config"
        ), patch.object(registry, "_initialize_providers"), patch.object(
            registry, "_save_config"
        ):
            await registry.initialize()

            assert registry._initialized == True
            assert isinstance(registry.models, dict)
            assert isinstance(registry.providers, dict)

    @pytest.mark.asyncio
    async def test_model_registration(self):
        """Test model registration"""
        registry = ModelRegistry()

        model_data = {
            "name": "test-model",
            "provider": "test-provider",
            "context_size": 4096,
            "capabilities": ["test"],
        }

        with patch.object(registry, "_save_config"):
            success = await registry.register_model(model_data)

            assert success == True
            assert "test-model" in registry.models
            assert registry.models["test-model"].name == "test-model"


class TestMetricsCollector:
    """Test Metrics Collector functionality"""

    @pytest.mark.asyncio
    async def test_metrics_initialization(self):
        """Test metrics collector initialization"""
        collector = MetricsCollector()

        await collector.initialize()

        assert collector._initialized == True
        assert isinstance(collector.request_metrics, list)
        assert isinstance(collector.model_metrics, dict)

    @pytest.mark.asyncio
    async def test_record_request(self):
        """Test request recording"""
        collector = MetricsCollector()

        await collector.record_request(
            model_name="test-model",
            latency_ms=1000,
            tokens_used=100,
            cost=0.01,
            success=True,
        )

        assert collector.total_requests == 1
        assert collector.successful_requests == 1
        assert "test-model" in collector.model_metrics


class TestTaskRouter:
    """Test Task Router functionality"""

    @pytest.mark.asyncio
    async def test_router_initialization(self):
        """Test router initialization"""
        registry = Mock()
        router = TaskRouter(registry)

        await router.initialize()

        assert router._initialized == True
        assert isinstance(router.routing_policies, dict)


class TestAgentCoordinator:
    """Test Agent Coordinator functionality"""

    @pytest.mark.asyncio
    async def test_coordinator_initialization(self):
        """Test coordinator initialization"""
        registry = Mock()
        router = Mock()
        coordinator = AgentCoordinator(registry, router)

        await coordinator.initialize()

        assert coordinator._initialized == True
        assert isinstance(coordinator.agents, dict)

    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Test agent creation"""
        registry = Mock()
        router = Mock()
        coordinator = AgentCoordinator(registry, router)

        agent_config = {
            "agent_id": "test-agent",
            "role": "analyst",
            "expertise": ["analysis"],
        }

        agent_id = await coordinator.create_agent(agent_config)

        assert agent_id == "test-agent"
        assert "test-agent" in coordinator.agents


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running basic LM Hack Proxy tests...")

    async def run_tests():
        # Test registry
        registry = TestModelRegistry()
        await registry.test_registry_initialization()
        await registry.test_model_registration()
        print("[OK] Model Registry tests passed")

        # Test metrics
        metrics = TestMetricsCollector()
        await metrics.test_metrics_initialization()
        await metrics.test_record_request()
        print("[OK] Metrics Collector tests passed")

        # Test router
        router = TestTaskRouter()
        await router.test_router_initialization()
        print("[OK] Task Router tests passed")

        # Test coordinator
        coordinator = TestAgentCoordinator()
        await coordinator.test_coordinator_initialization()
        await coordinator.test_agent_creation()
        print("[OK] Agent Coordinator tests passed")

        print("🎉 All basic tests passed!")

    asyncio.run(run_tests())
