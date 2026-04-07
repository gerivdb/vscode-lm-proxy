"""
Automatically extracted TestModelRegistry class
"""


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
