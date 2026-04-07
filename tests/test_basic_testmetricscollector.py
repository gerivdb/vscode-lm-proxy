"""
Automatically extracted TestMetricsCollector class
"""


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
