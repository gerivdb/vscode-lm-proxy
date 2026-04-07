"""
Automatically extracted TaskRouter class
"""


class TaskRouter:
    """
    Intelligent task router that selects optimal models based on:
    - Task type and complexity
    - Performance requirements (latency, cost)
    - Model capabilities and availability
    - Historical performance data
    """

    def __init__(self, model_registry: ModelRegistry):
        super().__init__()
        self.registry = model_registry
        self.policies = RoutingPolicies()
        self.performance_history = PerformanceHistory()
        self.decision_engine = RoutingDecisionEngine(
            self.policies.get_routing_policies(),
            self.performance_history.performance_history,
        )
        self.executor = QueryExecutor(model_registry)
        self._initialized = False

    async def initialize(self):
        """Initialize the task router"""
        if self._initialized:
            return
        logger.info("Initializing Task Router...")
        self._initialized = True
        logger.info("Task Router initialized")

    async def close(self):
        """Cleanup resources"""
        logger.info("Closing Task Router...")

    async def route_query(
        self,
        prompt: str,
        model: Optional[str] = None,
        task_metadata: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[QueryResult]:
        """
        Route a query to the optimal model
        """
        start_time = time.time()
        try:
            if model:
                result = await self.executor.execute_query(
                    model, prompt, options, start_time
                )
                return result

            candidates = await self.registry.get_models_for_task(
                (
                    task_metadata.get("task_type", "general")
                    if task_metadata
                    else "general"
                ),
                task_metadata.get("context_size", 4096) if task_metadata else 4096,
            )
            decision = await self.decision_engine.make_decision(
                prompt, task_metadata, candidates
            )
            if not decision:
                logger.warning("No suitable model found for query")
                return None

            result = await self.executor.execute_query(
                decision.selected_model, prompt, options, start_time
            )
            if result:
                result.routing_decision = decision
                self.performance_history.record_performance(
                    decision.selected_model,
                    result.latency_ms,
                    result.tokens_used,
                    result.cost,
                )
            return result
        except Exception as e:
            logger.error(f"Query routing failed: {e}")
            return None

    async def batch_route_queries(
        self,
        prompts: List[str],
        task_metadata: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Optional[QueryResult]]:
        """
        Route multiple queries in batch for efficiency
        """
        if not prompts:
            return []
        start_time = time.time()
        try:
            candidates = await self.registry.get_models_for_task(
                (
                    task_metadata.get("task_type", "general")
                    if task_metadata
                    else "general"
                ),
                task_metadata.get("context_size", 4096) if task_metadata else 4096,
            )
            decision = await self.decision_engine.make_decision(
                prompts[0], task_metadata, candidates
            )
            if not decision:
                logger.warning("No suitable model found for batch queries")
                return [None] * len(prompts)

            tasks = [
                self.executor.execute_query(
                    decision.selected_model, prompt, options, start_time
                )
                for prompt in prompts
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch query {i} failed: {result}")
                    processed_results.append(None)
                elif isinstance(result, QueryResult):
                    result.routing_decision = decision
                    self.performance_history.record_performance(
                        decision.selected_model,
                        result.latency_ms,
                        result.tokens_used,
                        result.cost,
                    )
                    processed_results.append(result)
                else:
                    processed_results.append(None)
            return processed_results
        except Exception as e:
            logger.error(f"Batch routing failed: {e}")
            return [None] * len(prompts)

    async def get_routing_policies(self) -> Dict[str, Any]:
        """Get current routing policies"""
        return self.policies.get_routing_policies()

    async def update_routing_policies(self, policies: Dict[str, Any]) -> bool:
        """Update routing policies"""
        return self.policies.update_routing_policies(policies)
