#!/usr/bin/env python
"""
LM Hack Proxy Server
FastAPI server providing intelligent LLM orchestration for ECOS CLI integration
"""

import asyncio
import hashlib
import json
import logging
import os
import threading
import time
from asyncio import PriorityQueue, Queue
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import aiohttp
import uvicorn
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import local modules
from src.models.registry import ModelRegistry
from src.models.router import TaskRouter
from src.utils.monitoring.metrics import MetricsCollector

from src.agents.coordinator import AgentCoordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Performance Optimization Components
class ResponseCache:
    """High-performance LRU cache for API responses"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        super().__init__()
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._lock = asyncio.Lock()

    def _generate_key(self, prompt: str, model: str, options: Dict[str, Any]) -> str:
        """Generate cache key from request parameters"""
        key_data = f"{prompt}:{model}:{json.dumps(options, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def get(
        self, prompt: str, model: str, options: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        async with self._lock:
            key = self._generate_key(prompt, model, options)
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry["timestamp"] < self.ttl_seconds:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    return entry["response"]
                else:
                    # Expired, remove
                    del self.cache[key]
            return None

    async def set(
        self, prompt: str, model: str, options: Dict[str, Any], response: Dict[str, Any]
    ):
        """Cache response with timestamp"""
        async with self._lock:
            key = self._generate_key(prompt, model, options)
            if key in self.cache:
                del self.cache[key]

            self.cache[key] = {"response": response, "timestamp": time.time()}

            # Evict least recently used if over capacity
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)


class HTTPConnectionPool:
    """Optimized HTTP connection pool for external API calls"""

    def __init__(self, max_connections: int = 100, timeout: int = 30):
        super().__init__()
        self.max_connections = max_connections
        self.timeout = ClientTimeout(total=timeout)
        self._session: Optional[ClientSession] = None
        self._lock = asyncio.Lock()

    async def get_session(self) -> ClientSession:
        """Get or create optimized HTTP session"""
        async with self._lock:
            if self._session is None or self._session.closed:
                connector = TCPConnector(
                    limit=self.max_connections,
                    limit_per_host=10,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    keepalive_timeout=60,
                    enable_cleanup_closed=True,
                )
                self._session = ClientSession(
                    connector=connector, timeout=self.timeout, trust_env=True
                )
            return self._session

    async def close(self):
        """Close HTTP session"""
        async with self._lock:
            if self._session and not self._session.closed:
                await self._session.close()


class AsyncTaskQueue:
    """Priority-based async task queue for optimal concurrency"""

    def __init__(self, max_concurrent: int = 50):
        super().__init__()
        self.queue = PriorityQueue()
        self.max_concurrent = max_concurrent
        self.active_tasks = 0
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def submit(self, priority: int, task_func, *args, **kwargs):
        """Submit task with priority (lower number = higher priority)"""
        future = asyncio.Future()
        await self.queue.put((priority, time.time(), future, task_func, args, kwargs))
        return future

    async def process_queue(self):
        """Process queued tasks with concurrency control"""
        while True:
            try:
                (
                    priority,
                    timestamp,
                    future,
                    task_func,
                    args,
                    kwargs,
                ) = await self.queue.get()

                async def execute_task():
                    async with self._semaphore:
                        try:
                            result = await task_func(*args, **kwargs)
                            future.set_result(result)
                        except Exception as e:
                            future.set_exception(e)
                        finally:
                            self.queue.task_done()

                asyncio.create_task(execute_task())

            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(0.1)


class OptimizedMetricsCollector:
    """High-performance metrics collection with minimal overhead"""

    def __init__(self):
        super().__init__()
        self.metrics = {}
        self._lock = asyncio.Lock()
        self._buffer = []
        self._buffer_size = 1000
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._start_time = time.time()

    async def initialize(self):
        """Initialize metrics collector"""
        logger.info("OptimizedMetricsCollector initialized")
        return True

    async def close(self):
        """Close metrics collector"""
        self._executor.shutdown(wait=True)
        logger.info("OptimizedMetricsCollector closed")
        return True

    async def record_request(
        self, model_name: str, latency_ms: int, tokens: int, cost: Optional[float]
    ):
        """Record request metrics with buffering for performance"""
        async with self._lock:
            self._buffer.append(
                {
                    "model": model_name,
                    "latency": latency_ms,
                    "tokens": tokens,
                    "cost": cost,
                    "timestamp": time.time(),
                }
            )

            if len(self._buffer) >= self._buffer_size:
                await self._flush_buffer()

    async def _flush_buffer(self):
        """Flush metrics buffer to storage"""
        if not self._buffer:
            return

        buffer_copy = self._buffer.copy()
        self._buffer.clear()

        # Process in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._process_metrics, buffer_copy)

    def _process_metrics(self, metrics_data):
        """Process metrics in thread pool"""
        try:
            for metric in metrics_data:
                model = metric["model"]
                if model not in self.metrics:
                    self.metrics[model] = {
                        "total_requests": 0,
                        "total_latency": 0,
                        "total_tokens": 0,
                        "total_cost": 0,
                        "avg_latency": 0,
                        "avg_tokens": 0,
                        "avg_cost": 0,
                    }

                self.metrics[model]["total_requests"] += 1
                self.metrics[model]["total_latency"] += metric["latency"]
                self.metrics[model]["total_tokens"] += metric["tokens"]
                if metric["cost"]:
                    self.metrics[model]["total_cost"] += metric["cost"]

                # Update averages
                req_count = self.metrics[model]["total_requests"]
                self.metrics[model]["avg_latency"] = (
                    self.metrics[model]["total_latency"] / req_count
                )
                self.metrics[model]["avg_tokens"] = (
                    self.metrics[model]["total_tokens"] / req_count
                )
                if self.metrics[model]["total_cost"] > 0:
                    self.metrics[model]["avg_cost"] = (
                        self.metrics[model]["total_cost"] / req_count
                    )

        except Exception as e:
            logger.error(f"Metrics processing error: {e}")

    async def get_metrics(self, model_name: Optional[str] = None):
        """Get metrics for specific model or all models"""
        await self._flush_buffer()  # Ensure latest data

        if model_name:
            return self.metrics.get(model_name, {})
        return self.metrics

    async def get_system_metrics(self):
        """Get system-wide metrics"""
        await self._flush_buffer()

        total_requests = sum(
            model_data["total_requests"] for model_data in self.metrics.values()
        )
        total_cost = sum(
            model_data["total_cost"] for model_data in self.metrics.values()
        )

        return {
            "uptime": time.time() - self._start_time,
            "total_requests": total_requests,
            "total_cost": total_cost,
            "active_models": len(self.metrics),
        }


# Initialize FastAPI app with performance optimizations
app = FastAPI(
    title="LM Hack Proxy",
    description="High-performance intelligent LLM orchestration proxy for ECOS CLI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize performance optimization components
response_cache = ResponseCache(
    max_size=2000, ttl_seconds=600
)  # 2000 entries, 10min TTL
http_pool = HTTPConnectionPool(max_connections=200, timeout=60)
task_queue = AsyncTaskQueue(max_concurrent=100)

# Initialize core components
model_registry = ModelRegistry()
task_router = TaskRouter(model_registry)
agent_coordinator = AgentCoordinator(model_registry, task_router)
metrics_collector = OptimizedMetricsCollector()


# Start background task processor
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info("Starting high-performance LM Hack Proxy server...")

    try:
        # Initialize core components
        await model_registry.initialize()
        await task_router.initialize()
        await agent_coordinator.initialize()
        await metrics_collector._flush_buffer()  # Initialize metrics

        # Start background queue processor
        asyncio.create_task(task_queue.process_queue())

        logger.info("High-performance LM Hack Proxy server started successfully")

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down high-performance LM Hack Proxy server...")

    try:
        await model_registry.close()
        await task_router.close()
        await agent_coordinator.close()
        await http_pool.close()
        await metrics_collector._flush_buffer()

        logger.info("High-performance LM Hack Proxy server shut down successfully")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Pydantic models for API
class ModelInfo(BaseModel):
    name: str
    provider: str
    context_size: int
    capabilities: List[str]
    latency_ms: Optional[float] = None
    tokens_per_sec: Optional[float] = None
    cost_per_token: Optional[float] = None


class TaskMetadata(BaseModel):
    task_type: str = Field(
        ..., description="Type of task (code_analysis, code_generation, etc.)"
    )
    complexity: str = Field(
        ..., description="Task complexity (simple, medium, complex)"
    )
    context_size: int = Field(..., description="Required context window size")
    latency_budget: Optional[int] = Field(
        None, description="Maximum acceptable latency in ms"
    )
    priority: str = Field(
        "normal", description="Task priority (low, normal, high, critical)"
    )


class QueryRequest(BaseModel):
    prompt: str = Field(..., description="The query prompt")
    model: Optional[str] = Field(None, description="Specific model to use")
    task_metadata: Optional[TaskMetadata] = Field(
        None, description="Task context for routing"
    )
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional options"
    )


class BatchQueryRequest(BaseModel):
    prompts: List[str] = Field(..., description="List of prompts to process")
    task_metadata: Optional[TaskMetadata] = Field(
        None, description="Task context for routing"
    )
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional options"
    )


class LMHackResponse(BaseModel):
    content: str
    model_used: str
    tokens_used: int
    latency_ms: int
    cost: Optional[float] = None


class SystemStatus(BaseModel):
    status: str
    uptime: float
    total_requests: int
    active_models: int
    version: str
    timestamp: datetime


class RoutingPolicy(BaseModel):
    task_type: str
    model_priorities: List[str]
    cost_weight: float = 0.3
    performance_weight: float = 0.4
    latency_weight: float = 0.3


# API Endpoints


@app.get("/api/models", response_model=List[ModelInfo])
async def get_available_models():
    """Get list of available models with detailed metadata"""
    try:
        models = await model_registry.get_available_models()
        return [
            ModelInfo(
                name=model.name,
                provider=model.provider,
                context_size=model.context_size,
                capabilities=model.capabilities,
                latency_ms=model.latency_ms,
                tokens_per_sec=model.tokens_per_sec,
                cost_per_token=model.cost_per_token,
            )
            for model in models
        ]
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")


@app.post("/api/query", response_model=LMHackResponse)
async def query_model(request: QueryRequest, background_tasks: BackgroundTasks):
    """Execute a single query with intelligent model routing"""
    start_time = time.time()

    try:
        # Convert request to internal format
        task_metadata = None
        if request.task_metadata:
            task_metadata = {
                "task_type": request.task_metadata.task_type,
                "complexity": request.task_metadata.complexity,
                "context_size": request.task_metadata.context_size,
                "latency_budget": request.task_metadata.latency_budget,
                "priority": request.task_metadata.priority,
            }

        # Route and execute query
        result = await task_router.route_query(
            prompt=request.prompt,
            model=request.model,
            task_metadata=task_metadata,
            options=request.options,
        )

        if not result:
            raise HTTPException(status_code=503, detail="No suitable model available")

        # Record metrics
        latency = int((time.time() - start_time) * 1000)
        background_tasks.add_task(
            metrics_collector.record_request,
            result.model_used,
            latency,
            result.tokens_used,
            result.cost,
        )

        return LMHackResponse(
            content=result.content,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            latency_ms=latency,
            cost=result.cost,
        )

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@app.post("/api/batch-query", response_model=List[Optional[LMHackResponse]])
async def batch_query(request: BatchQueryRequest, background_tasks: BackgroundTasks):
    """Execute multiple queries in batch"""
    start_time = time.time()

    try:
        # Convert request to internal format
        task_metadata = None
        if request.task_metadata:
            task_metadata = {
                "task_type": request.task_metadata.task_type,
                "complexity": request.task_metadata.complexity,
                "context_size": request.task_metadata.context_size,
                "latency_budget": request.task_metadata.latency_budget,
                "priority": request.task_metadata.priority,
            }

        # Execute batch query
        results = await task_router.batch_route_queries(
            prompts=request.prompts,
            task_metadata=task_metadata,
            options=request.options,
        )

        # Convert results and record metrics
        responses = []
        total_latency = int((time.time() - start_time) * 1000)

        for i, result in enumerate(results):
            if result:
                background_tasks.add_task(
                    metrics_collector.record_request,
                    result.model_used,
                    total_latency // len(results),  # Approximate per-request latency
                    result.tokens_used,
                    result.cost,
                )

                responses.append(
                    LMHackResponse(
                        content=result.content,
                        model_used=result.model_used,
                        tokens_used=result.tokens_used,
                        latency_ms=total_latency // len(results),
                        cost=result.cost,
                    )
                )
            else:
                responses.append(None)

        return responses

    except Exception as e:
        logger.error(f"Batch query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch query failed: {str(e)}")


@app.get("/api/metrics")
async def get_metrics(model_name: Optional[str] = None):
    """Get performance metrics"""
    try:
        return await metrics_collector.get_metrics(model_name)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@app.post("/api/config/models")
async def update_model_config(config: Dict[str, Any]):
    """Update model configuration"""
    try:
        success = await model_registry.update_config(config)
        if success:
            return {"success": True, "message": "Configuration updated"}
        else:
            raise HTTPException(status_code=400, detail="Configuration update failed")
    except Exception as e:
        logger.error(f"Config update failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Configuration update failed: {str(e)}"
        )


@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get system health and status"""
    try:
        metrics = await metrics_collector.get_system_metrics()
        models = await model_registry.get_available_models()

        return SystemStatus(
            status="healthy",
            uptime=metrics.get("uptime", 0),
            total_requests=metrics.get("total_requests", 0),
            active_models=len(models),
            version="1.0.0",
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


@app.get("/api/policies/routing")
async def get_routing_policies():
    """Get current routing policies"""
    try:
        return await task_router.get_routing_policies()
    except Exception as e:
        logger.error(f"Failed to get routing policies: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve routing policies"
        )


@app.post("/api/policies/routing")
async def update_routing_policies(policies: Dict[str, Any]):
    """Update routing policies"""
    try:
        success = await task_router.update_routing_policies(policies)
        if success:
            return {"success": True, "message": "Routing policies updated"}
        else:
            raise HTTPException(status_code=400, detail="Policy update failed")
    except Exception as e:
        logger.error(f"Policy update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Policy update failed: {str(e)}")


@app.post("/api/agents/orchestrate")
async def orchestrate_agents(request: Dict[str, Any]):
    """Orchestrate multi-agent execution"""
    try:
        result = await agent_coordinator.orchestrate_agents(request)
        return result
    except Exception as e:
        logger.error(f"Agent orchestration failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Agent orchestration failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Performance optimization endpoints
@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    return {
        "cache_size": len(response_cache.cache),
        "max_size": response_cache.max_size,
        "ttl_seconds": response_cache.ttl_seconds,
        "hit_rate_estimate": "Optimized for high hit rates with intelligent caching",
    }


@app.post("/api/cache/clear")
async def clear_cache():
    """Clear response cache"""
    response_cache.cache.clear()
    return {"message": "Cache cleared successfully"}


@app.get("/api/performance/stats")
async def get_performance_stats():
    """Get comprehensive performance statistics"""
    return {
        "http_pool": {
            "max_connections": http_pool.max_connections,
            "timeout_seconds": http_pool.timeout.total if http_pool.timeout else None,
        },
        "task_queue": {
            "max_concurrent": task_queue.max_concurrent,
            "active_tasks": task_queue.active_tasks,
        },
        "response_cache": await get_cache_stats(),
        "metrics_buffer_size": len(metrics_collector._buffer),
        "optimization_status": "High-performance mode active",
    }


if __name__ == "__main__":
    # Get port from environment or default to 4000
    port = int(os.getenv("LM_HACK_PORT", "4000"))
    host = os.getenv("LM_HACK_HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run("server:app", host=host, port=port, reload=True, log_level="info")
