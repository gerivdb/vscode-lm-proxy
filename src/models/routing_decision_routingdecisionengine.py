"""
Automatically extracted RoutingDecisionEngine class
"""


class RoutingDecisionEngine:
    """
    Encapsulates logic for scoring models and making routing decisions.
    """

    def __init__(
        self,
        routing_policies: Dict[str, Dict[str, Any]],
        performance_history: Dict[str, List[Dict[str, Any]]],
    ):
        super().__init__()
        self.routing_policies = routing_policies
        self.performance_history = performance_history

    async def make_decision(
        self,
        prompt: str,
        task_metadata: Optional[Dict[str, Any]],
        candidates: List[ModelMetadata],
    ) -> Optional[RoutingDecision]:
        """
        Make intelligent routing decision based on task requirements and candidates.
        """
        # Extract task requirements
        task_type = (
            task_metadata.get("task_type", "general") if task_metadata else "general"
        )
        complexity = (
            task_metadata.get("complexity", "medium") if task_metadata else "medium"
        )
        context_size = (
            task_metadata.get("context_size", 4096) if task_metadata else 4096
        )
        latency_budget = task_metadata.get("latency_budget") if task_metadata else None
        priority = (
            task_metadata.get("priority", "normal") if task_metadata else "normal"
        )

        # Score candidates
        scored_candidates = []
        for model in candidates:
            score, reasoning = await self.score_model_for_task(
                model, task_type, complexity, context_size, latency_budget, priority
            )
            scored_candidates.append((model, score, reasoning))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        if not scored_candidates:
            return None

        best_model, best_score, reasoning = scored_candidates[0]
        alternatives = [model.name for model, _, _ in scored_candidates[1:3]]
        estimated_latency = best_model.latency_ms or 2000
        estimated_cost = await self.estimate_cost(best_model, prompt)

        return RoutingDecision(
            selected_model=best_model.name,
            confidence_score=min(best_score / 100.0, 1.0),
            reasoning=reasoning,
            alternatives=alternatives,
            estimated_latency=estimated_latency,
            estimated_cost=estimated_cost,
        )

    async def score_model_for_task(
        self,
        model: ModelMetadata,
        task_type: str,
        complexity: str,
        context_size: int,
        latency_budget: Optional[int],
        priority: str,
    ) -> Tuple[float, str]:
        """
        Score a model for a specific task based on multiple criteria.
        """
        score = 0.0
        reasons = []

        # Base capability score (0-40 points)
        task_policy = self.routing_policies.get(task_type, {})
        model_priority = task_policy.get("model_priorities", [])

        if model.name in model_priority:
            priority_index = model_priority.index(model.name)
            capability_score = max(40 - (priority_index * 10), 10)
            score += capability_score
            reasons.append(f"High priority for {task_type} (+{capability_score})")
        else:
            required_caps = task_policy.get("required_capabilities", [])
            if required_caps and any(
                cap in model.capabilities for cap in required_caps
            ):
                score += 25
                reasons.append("Has required capabilities (+25)")
            else:
                score += 10
                reasons.append("Basic capability match (+10)")

        # Performance score (0-30 points)
        if model.latency_ms:
            if latency_budget and model.latency_ms <= latency_budget:
                perf_score = 30
                reasons.append(f"Within latency budget (+30)")
            elif not latency_budget:
                if model.latency_ms < 2000:
                    perf_score = 25
                    reasons.append("Fast model (+25)")
                elif model.latency_ms < 3000:
                    perf_score = 20
                    reasons.append("Moderate speed (+20)")
                else:
                    perf_score = 15
                    reasons.append("Slower model (+15)")
            else:
                perf_score = 10
                reasons.append("Exceeds latency budget (+10)")
            score += perf_score

        # Cost optimization score (0-20 points)
        if model.cost_per_token:
            cost_score = max(20 - (model.cost_per_token * 100000), 5)
            if priority == "high" or priority == "critical":
                cost_score *= 0.7
            score += cost_score
            reasons.append(f"Cost efficiency (+{cost_score:.1f})")

        # Historical performance score (0-10 points)
        history_score = await self.get_historical_performance_score(model.name)
        if history_score > 0:
            score += history_score
            reasons.append(f"Historical performance (+{history_score})")

        # Complexity matching (0-10 points)
        if complexity == "simple" and model.latency_ms and model.latency_ms < 1500:
            score += 10
            reasons.append("Good for simple tasks (+10)")
        elif complexity == "complex" and model.context_size >= context_size:
            score += 10
            reasons.append("Good for complex tasks (+10)")
        elif complexity == "medium":
            score += 5
            reasons.append("Balanced for medium tasks (+5)")

        reasoning = "; ".join(reasons)
        return score, reasoning

    async def estimate_cost(self, model: ModelMetadata, prompt: str) -> float:
        """Estimate cost for a query"""
        if not model.cost_per_token:
            return 0.0
        estimated_tokens = len(prompt.split()) * 1.3
        return estimated_tokens * model.cost_per_token

    async def get_historical_performance_score(self, model_name: str) -> float:
        """Get performance score based on historical data"""
        history = self.performance_history.get(model_name, [])
        if not history:
            return 0.0
        avg_latency = sum(h["latency_ms"] for h in history) / len(history)
        latency_score = max(10 - (avg_latency / 500), 0)
        success_score = 5
        return latency_score + success_score
