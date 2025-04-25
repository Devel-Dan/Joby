import pytest
import asyncio
from unittest.mock import AsyncMock
from joby_challenge.models.async_worker_pool import AsyncWorkerPool, DEFAULT_MAX_CONCURRENT_WORKERS
from tests.constants import TEST_EXCEPTION_MESSAGE, TEST_MAX_CONCURRENT

TEST_QUEUE_ITEM = "test_item"
TEST_ITEMS = ["item1", "item2", "item3"]
TEST_SLEEP_TIME = 0.1
WORKER_TEST_CASES = [
    (True, None, True),
    (None, Exception(TEST_EXCEPTION_MESSAGE), False),
]
START_TEST_CASES = [(TEST_ITEMS, len(TEST_ITEMS)), ([], 0), (["single_item"], 1)]


class TestAsyncWorkerPool:

    @pytest.mark.asyncio
    async def test_async_worker_pool_init(self, target_function, result_callback):
        """ tests initialization"""
        # Test initialization with default max_concurrent
        pool = AsyncWorkerPool(target_function, result_callback)
        assert pool.target_function == target_function
        assert pool.result_callback == result_callback
        assert pool.concurrent_workers == DEFAULT_MAX_CONCURRENT_WORKERS
        assert isinstance(pool.queue, asyncio.Queue)
        assert pool.workers == []

        # Test initialization with custom max_concurrent
        pool = AsyncWorkerPool(
            target_function, result_callback, max_concurrent=TEST_MAX_CONCURRENT
        )
        assert pool.concurrent_workers == TEST_MAX_CONCURRENT

    @pytest.mark.parametrize(
        "func_return,func_side_effect,expected_callback_result",
        WORKER_TEST_CASES,
        ids=["success", "exception raised"],
    )
    @pytest.mark.asyncio
    async def test_worker(
        self, result_callback, func_return, func_side_effect, expected_callback_result
    ):
        """Test that worker processes queue items correctly"""
        # Create target function based on parameters
        if func_side_effect:
            target_function = AsyncMock(side_effect=func_side_effect)
        else:
            target_function = AsyncMock(return_value=func_return)

        pool = AsyncWorkerPool(target_function, result_callback)

        # Add an item to the queue
        await pool.queue.put(TEST_QUEUE_ITEM)

        # Start a worker task
        worker_task = asyncio.create_task(pool.worker())

        # Wait a bit for the worker to process the item
        await asyncio.sleep(TEST_SLEEP_TIME)

        # Check that the target function was called with the item
        target_function.assert_called_once_with(TEST_QUEUE_ITEM)

        # Check that the result callback was called with the item and expected result
        result_callback.assert_called_once_with(
            TEST_QUEUE_ITEM, expected_callback_result
        )

        # Cancel the worker task
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_populate_queue(self, pool):
        """Test that populate_queue correctly adds items to the queue."""
        # Populate the queue with items
        await pool.populate_queue(TEST_ITEMS)

        # Check that the queue has the expected size
        assert pool.queue.qsize() == len(TEST_ITEMS)

        # Check that the items are in the queue
        for expected_item in TEST_ITEMS:
            assert await pool.queue.get() == expected_item

    @pytest.mark.parametrize(
        "items,expected_calls",
        START_TEST_CASES,
        ids=["multiple items", "no items", "single item"],
    )
    @pytest.mark.asyncio
    async def test_start(self, target_function, result_callback, items, expected_calls):
        """Test that start correctly processes all items in the queue."""
        pool = AsyncWorkerPool(target_function, result_callback, max_concurrent=3)

        # Start the pool with items
        await pool.start(items)

        # Check that the target function was called the expected number of times
        assert target_function.call_count == expected_calls

        # Check that the result callback was called the expected number of times
        assert result_callback.call_count == expected_calls

        # If there were items, check that they were processed
        if items:
            for item in items:
                target_function.assert_any_call(item)
                result_callback.assert_any_call(item, True)
