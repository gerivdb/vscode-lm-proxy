"""
Automatically extracted TestTaskRouter class
"""


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
