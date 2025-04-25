import asyncio
import logging

logger = logging.getLogger("AsyncWorkerPool")

# Default value
DEFAULT_MAX_CONCURRENT_WORKERS = 50

class AsyncWorkerPool:
    """
    Manages asynchronous workers and task queue without any data collection.
    """
    def __init__(self, target_function, result_callback, max_concurrent=DEFAULT_MAX_CONCURRENT_WORKERS):
        self.target_function = target_function
        self.result_callback = result_callback 
        self.queue = asyncio.Queue()
        self.workers = []
        self.concurrent_workers = max_concurrent

    async def worker(self):
        """Process tasks from the queue without storing results."""
        while True:
            argument = await self.queue.get()
            try:
                result = await self.target_function(argument)
                # Pass result to callback instead of storing locally
                self.result_callback(argument, result)
            except Exception as e:
                self.result_callback(argument, False)
                logger.debug(f"Task failed for {argument}: {str(e)}")
            finally:
                self.queue.task_done()

    async def populate_queue(self, items):
        """Add items to the queue."""
        for item in items:
            await self.queue.put(item)

    async def start(self, items=None):
        """Start processing items from the queue."""
        # Add items to the queue if provided
        if items:
            await self.populate_queue(items)
            
        # Adjust worker count if needed
        worker_count = min(self.concurrent_workers, self.queue.qsize())
        
        # Create workers
        for _ in range(worker_count):
            worker = asyncio.create_task(self.worker())
            self.workers.append(worker)

        # Wait for queue to be processed
        await self.queue.join()

        # Cancel workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to be cancelled
        await asyncio.gather(*self.workers, return_exceptions=True)