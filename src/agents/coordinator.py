"""
Agent Coordinator
Manages multi-agent orchestration for complex tasks
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models.registry import ModelRegistry
from ..models.router import TaskRouter

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an agent"""

    agent_id: str
    role: str
    expertise: List[str] = field(default_factory=list)
    model_preference: Optional[str] = None
    max_iterations: int = 3
    temperature: float = 0.7


@dataclass
class AgentTask:
    """A task assigned to an agent"""

    task_id: str
    agent_id: str
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    priority: int = 1
    timeout_seconds: int = 300


@dataclass
class AgentResult:
    """Result from an agent execution"""

    task_id: str
    agent_id: str
    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCoordinator:
    """
    Coordinates multiple agents for complex multi-agent workflows
    Supports sequential, parallel, and hierarchical execution patterns
    """

    def __init__(self, model_registry: ModelRegistry, task_router: TaskRouter):
        super().__init__()
        self.registry = model_registry
        self.router = task_router
        self.agents: Dict[str, AgentConfig] = {}
        self.active_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: Dict[str, AgentResult] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize the agent coordinator"""
        if self._initialized:
            return

        logger.info("Initializing Agent Coordinator...")
        self._initialized = True
        logger.info("Agent Coordinator initialized")

    async def close(self):
        """Cleanup resources"""
        logger.info("Closing Agent Coordinator...")

    async def orchestrate_agents(
        self, orchestration_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate a multi-agent workflow

        Args:
            orchestration_request: Request containing workflow specification

        Returns:
            Orchestration results
        """

        try:
            # Parse request
            strategy = orchestration_request.get("strategy", "sequential")
            main_task = orchestration_request.get("task", "")
            task_metadata = orchestration_request.get("task_metadata", {})
            agent_configs = orchestration_request.get("agents", [])

            # Create agents
            agent_ids = []
            for agent_config in agent_configs:
                agent_id = await self.create_agent(agent_config)
                agent_ids.append(agent_id)

            # Execute based on strategy
            if strategy == "sequential":
                result = await self._execute_sequential(
                    main_task, agent_ids, task_metadata
                )
            elif strategy == "parallel":
                result = await self._execute_parallel(
                    main_task, agent_ids, task_metadata
                )
            elif strategy == "hierarchical":
                result = await self._execute_hierarchical(
                    main_task, agent_ids, task_metadata
                )
            elif strategy == "collaborative":
                result = await self._execute_collaborative(
                    main_task, agent_ids, task_metadata
                )
            else:
                result = await self._execute_sequential(
                    main_task, agent_ids, task_metadata
                )

            # Cleanup agents
            for agent_id in agent_ids:
                await self.remove_agent(agent_id)

            return {
                "success": True,
                "strategy": strategy,
                "result": result,
                "execution_time": result.get("execution_time", 0),
                "agents_used": len(agent_ids),
            }

        except Exception as e:
            logger.error(f"Agent orchestration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "strategy": orchestration_request.get("strategy", "unknown"),
            }

    async def create_agent(self, agent_config: Dict[str, Any]) -> str:
        """
        Create a new agent

        Args:
            agent_config: Agent configuration

        Returns:
            Agent ID
        """

        agent_id = agent_config.get("agent_id", f"agent_{len(self.agents)}")
        role = agent_config.get("role", "analyst")
        expertise = agent_config.get("expertise", [])
        model_preference = agent_config.get("model_preference")
        max_iterations = agent_config.get("max_iterations", 3)
        temperature = agent_config.get("temperature", 0.7)

        agent = AgentConfig(
            agent_id=agent_id,
            role=role,
            expertise=expertise,
            model_preference=model_preference,
            max_iterations=max_iterations,
            temperature=temperature,
        )

        self.agents[agent_id] = agent
        logger.info(f"Created agent {agent_id} with role {role}")
        return agent_id

    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent_id}")
            return True
        return False

    async def _execute_sequential(
        self, main_task: str, agent_ids: List[str], task_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute agents in sequence, each building on previous results
        """

        start_time = time.time()
        results = []
        current_context = task_metadata.copy()
        current_prompt = main_task

        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if not agent:
                continue

            # Create agent-specific prompt
            agent_prompt = await self._create_agent_prompt(
                agent, current_prompt, current_context, results
            )

            # Execute agent task
            result = await self._execute_agent_task(
                agent_id, agent_prompt, current_context
            )

            if result:
                results.append(result)

                # Update context with result
                current_context[f"{agent_id}_result"] = result.content
                current_context[f"{agent_id}_quality"] = result.quality_score

                # Build on previous results
                current_prompt = f"{main_task}\n\nPrevious work:\n" + "\n".join(
                    [f"Agent {r.agent_id}: {r.content[:200]}..." for r in results]
                )

        # Synthesize final result
        final_result = await self._synthesize_results(results, main_task)

        execution_time = time.time() - start_time

        return {
            "strategy": "sequential",
            "agent_results": [
                {
                    "agent_id": r.agent_id,
                    "content": r.content,
                    "quality_score": r.quality_score,
                    "model_used": r.model_used,
                    "latency_ms": r.latency_ms,
                }
                for r in results
            ],
            "final_result": final_result,
            "execution_time": execution_time,
            "quality_score": sum(r.quality_score for r in results)
            / max(len(results), 1),
        }

    async def _execute_parallel(
        self, main_task: str, agent_ids: List[str], task_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute all agents in parallel
        """

        start_time = time.time()

        # Create tasks for all agents
        tasks = []
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if not agent:
                continue

            agent_prompt = await self._create_agent_prompt(
                agent, main_task, task_metadata, []
            )

            task = self._execute_agent_task(agent_id, agent_prompt, task_metadata)
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_ids[i]} failed: {result}")
            elif result:
                valid_results.append(result)

        # Synthesize final result
        final_result = await self._synthesize_results(valid_results, main_task)

        execution_time = time.time() - start_time

        return {
            "strategy": "parallel",
            "agent_results": [
                {
                    "agent_id": r.agent_id,
                    "content": r.content,
                    "quality_score": r.quality_score,
                    "model_used": r.model_used,
                    "latency_ms": r.latency_ms,
                }
                for r in valid_results
            ],
            "final_result": final_result,
            "execution_time": execution_time,
            "quality_score": sum(r.quality_score for r in valid_results)
            / max(len(valid_results), 1),
        }

    async def _execute_hierarchical(
        self, main_task: str, agent_ids: List[str], task_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute in hierarchical pattern with task decomposition
        """

        start_time = time.time()

        # First agent decomposes the task
        if not agent_ids:
            return {"error": "No agents available"}

        coordinator_id = agent_ids[0]  # First agent is coordinator
        worker_ids = agent_ids[1:]  # Rest are workers

        # Task decomposition
        decomposition = await self._decompose_task(
            coordinator_id, main_task, task_metadata
        )

        # Execute subtasks in parallel
        subtask_results = []
        if decomposition and "subtasks" in decomposition:
            tasks = []
            for i, subtask in enumerate(decomposition["subtasks"]):
                if i < len(worker_ids):
                    worker_id = worker_ids[i]
                    task = self._execute_agent_task(
                        worker_id,
                        subtask["prompt"],
                        {**task_metadata, "subtask_id": subtask["id"]},
                    )
                    tasks.append(task)

            # Execute subtasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Subtask {i} failed: {result}")
                elif result:
                    subtask_results.append(result)

        # Coordinator synthesizes results
        synthesis_prompt = f"""
        Original task: {main_task}

        Subtask results:
        {json.dumps([{'agent': r.agent_id, 'result': r.content} for r in subtask_results], indent=2)}

        Please synthesize a comprehensive solution that addresses the original task
        using the results from all subtasks.
        """

        final_result = await self._execute_agent_task(
            coordinator_id, synthesis_prompt, task_metadata
        )

        execution_time = time.time() - start_time

        return {
            "strategy": "hierarchical",
            "decomposition": decomposition,
            "subtask_results": [
                {
                    "agent_id": r.agent_id,
                    "content": r.content,
                    "quality_score": r.quality_score,
                }
                for r in subtask_results
            ],
            "final_result": final_result.content if final_result else None,
            "execution_time": execution_time,
            "quality_score": final_result.quality_score if final_result else 0.0,
        }

    async def _execute_collaborative(
        self, main_task: str, agent_ids: List[str], task_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute in collaborative iterative improvement pattern
        """

        start_time = time.time()
        max_iterations = 3
        best_result = None
        best_quality = 0.0

        for iteration in range(max_iterations):
            iteration_results = []

            # Each agent improves upon current best
            tasks = []
            for agent_id in agent_ids:
                agent = self.agents.get(agent_id)
                if not agent:
                    continue

                # Create collaborative prompt
                context = f"Current best quality: {best_quality}"
                if best_result:
                    context += (
                        f"\nCurrent best solution: {best_result.content[:500]}..."
                    )

                collab_prompt = f"""
                {main_task}

                {context}

                Iteration {iteration + 1}/{max_iterations}
                Your role: {agent.role}
                Your expertise: {', '.join(agent.expertise)}

                Please improve upon the current solution or provide a new approach.
                Focus on quality, accuracy, and innovation.
                """

                task = self._execute_agent_task(agent_id, collab_prompt, task_metadata)
                tasks.append(task)

            # Execute iteration
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Find best result this iteration
            for result in results:
                if isinstance(result, Exception):
                    continue
                elif result and result.quality_score > best_quality:
                    best_quality = result.quality_score
                    best_result = result
                    iteration_results.append(result)

            # Check convergence
            if best_quality > 0.8:  # Good enough quality
                break

        execution_time = time.time() - start_time

        return {
            "strategy": "collaborative",
            "iterations_completed": iteration + 1,
            "final_result": best_result.content if best_result else None,
            "quality_score": best_quality,
            "execution_time": execution_time,
            "converged": best_quality > 0.8,
        }

    async def _create_agent_prompt(
        self,
        agent: AgentConfig,
        task: str,
        context: Dict[str, Any],
        previous_results: List[AgentResult],
    ) -> str:
        """Create a specialized prompt for an agent"""

        prompt_parts = [
            f"You are an AI agent with role: {agent.role}",
            f"Your expertise areas: {', '.join(agent.expertise)}",
            "",
            f"Task: {task}",
            "",
            f"Context: {json.dumps(context, indent=2)}",
        ]

        if previous_results:
            prompt_parts.append("")
            prompt_parts.append("Previous agent results:")
            for result in previous_results:
                prompt_parts.append(
                    f"- Agent {result.agent_id}: {result.content[:200]}..."
                )

        prompt_parts.extend(
            [
                "",
                "Please provide a high-quality response that leverages your specific expertise.",
                "Focus on being accurate, helpful, and innovative in your approach.",
            ]
        )

        return "\n".join(prompt_parts)

    async def _execute_agent_task(
        self, agent_id: str, prompt: str, context: Dict[str, Any]
    ) -> Optional[AgentResult]:
        """Execute a task for a specific agent"""

        agent = self.agents.get(agent_id)
        if not agent:
            return None

        try:
            # Create task metadata for routing
            task_metadata = {
                "task_type": self._infer_task_type(prompt),
                "complexity": "medium",
                "context_size": len(prompt.split()) * 2,  # Rough estimate
                "priority": "normal",
            }

            # Route through task router
            result = await self.router.route_query(
                prompt=prompt,
                model=agent.model_preference,
                task_metadata=task_metadata,
                options={"temperature": agent.temperature},
            )

            if not result:
                return None

            # Assess quality (mock implementation)
            quality_score = await self._assess_result_quality(result.content, prompt)

            return AgentResult(
                task_id=f"{agent_id}_{int(time.time())}",
                agent_id=agent_id,
                content=result.content,
                model_used=result.model_used,
                tokens_used=result.tokens_used,
                latency_ms=result.latency_ms,
                cost=result.cost,
                quality_score=quality_score,
                metadata={"agent_role": agent.role, "expertise": agent.expertise},
            )

        except Exception as e:
            logger.error(f"Agent task execution failed for {agent_id}: {e}")
            return None

    async def _decompose_task(
        self, coordinator_id: str, main_task: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Decompose a complex task into subtasks"""

        decomposition_prompt = f"""
        You are a task decomposition specialist. Break down the following complex task into 3-5 manageable subtasks:

        Main Task: {main_task}

        Context: {json.dumps(context, indent=2)}

        Please provide a JSON response with the following structure:
        {{
            "subtasks": [
                {{
                    "id": "subtask_1",
                    "title": "Brief title",
                    "prompt": "Detailed prompt for this subtask",
                    "estimated_complexity": "simple|medium|complex",
                    "required_expertise": ["expertise1", "expertise2"]
                }}
            ],
            "coordination_notes": "How to combine the results"
        }}
        """

        result = await self._execute_agent_task(
            coordinator_id, decomposition_prompt, context
        )

        if result:
            try:
                return json.loads(result.content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse task decomposition JSON")

        # Fallback decomposition
        return {
            "subtasks": [
                {
                    "id": "analysis",
                    "title": "Problem Analysis",
                    "prompt": f"Analyze the following task: {main_task}",
                    "estimated_complexity": "medium",
                    "required_expertise": ["analysis"],
                },
                {
                    "id": "solution",
                    "title": "Solution Development",
                    "prompt": f"Develop a solution for: {main_task}",
                    "estimated_complexity": "medium",
                    "required_expertise": ["problem_solving"],
                },
                {
                    "id": "validation",
                    "title": "Solution Validation",
                    "prompt": f"Validate and improve the solution for: {main_task}",
                    "estimated_complexity": "simple",
                    "required_expertise": ["validation"],
                },
            ],
            "coordination_notes": "Combine analysis, solution, and validation into final result",
        }

    async def _synthesize_results(
        self, results: List[AgentResult], original_task: str
    ) -> str:
        """Synthesize multiple agent results into a final answer"""

        if not results:
            return "No results to synthesize"

        if len(results) == 1:
            return results[0].content

        # Use the first agent to synthesize (could be a dedicated synthesizer agent)
        synthesis_prompt = f"""
        Original Task: {original_task}

        Please synthesize the following agent results into a comprehensive, coherent final answer:

        {"".join([f"Agent {r.agent_id} ({r.metadata.get('agent_role', 'unknown')}): {r.content}\n\n" for r in results])}

        Provide a well-structured, comprehensive response that combines the best insights from all agents.
        """

        # Use first agent for synthesis
        synthesis_agent = results[0].agent_id
        synthesis_result = await self._execute_agent_task(
            synthesis_agent, synthesis_prompt, {}
        )

        return synthesis_result.content if synthesis_result else results[0].content

    async def _assess_result_quality(self, content: str, original_prompt: str) -> float:
        """Assess the quality of a result (mock implementation)"""

        # Simple quality heuristics
        score = 0.5  # Base score

        # Length appropriateness
        word_count = len(content.split())
        if 50 <= word_count <= 1000:
            score += 0.2

        # Structure indicators
        if any(
            indicator in content.lower()
            for indicator in ["therefore", "however", "furthermore", "conclusion"]
        ):
            score += 0.1

        # Completeness
        if content.endswith((".", "!", "?")):
            score += 0.1

        # Relevance (simple keyword matching)
        prompt_words = set(original_prompt.lower().split())
        content_words = set(content.lower().split())
        overlap = len(prompt_words.intersection(content_words))
        relevance_score = min(overlap / max(len(prompt_words), 1), 0.2)
        score += relevance_score

        return min(score, 1.0)

    def _infer_task_type(self, prompt: str) -> str:
        """Infer task type from prompt content"""

        prompt_lower = prompt.lower()

        # Code-related tasks
        if any(
            keyword in prompt_lower
            for keyword in ["code", "function", "class", "algorithm", "programming"]
        ):
            if "analyze" in prompt_lower or "review" in prompt_lower:
                return "code_analysis"
            elif (
                "generate" in prompt_lower
                or "create" in prompt_lower
                or "write" in prompt_lower
            ):
                return "code_generation"
            elif (
                "debug" in prompt_lower
                or "fix" in prompt_lower
                or "error" in prompt_lower
            ):
                return "debugging"
            elif "test" in prompt_lower:
                return "testing"
            else:
                return "code_generation"

        # Other task types
        elif any(
            keyword in prompt_lower for keyword in ["document", "explain", "describe"]
        ):
            return "documentation"
        elif any(
            keyword in prompt_lower
            for keyword in ["optimize", "improve", "performance"]
        ):
            return "optimization"
        elif any(keyword in prompt_lower for keyword in ["translate", "language"]):
            return "translation"
        else:
            return "general"
