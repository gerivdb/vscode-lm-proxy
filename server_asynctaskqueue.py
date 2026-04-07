"""
Automatically extracted AsyncTaskQueue class
"""


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
