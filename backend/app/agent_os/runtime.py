"""
Unified Async Runtime for Agent OS v2

Provides safe async execution in any context (Celery, FastAPI, WebSocket).
Ensures async functions can be called from sync contexts without event loop errors.
"""

import asyncio
import inspect
from typing import Any, Callable, Coroutine


def run_async_safe(func: Callable, *args, **kwargs) -> Any:
    """
    Execute async or sync function safely from any context (Celery, FastAPI, WebSocket).

    Args:
        func: The function to execute (can be async or sync)
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        The result of the function execution

    Raises:
        Exception: If the function raises an exception
    """
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create task if loop is already running
                return asyncio.create_task(result)
        except RuntimeError:
            pass
        # Run in new event loop if none exists or loop is not running
        return asyncio.run(result)
    return result


async def execute_node(node_func: Callable, context: dict) -> Any:
    """
    Execute a workflow node function with context.

    Args:
        node_func: The node function to execute (can be async or sync)
        context: Dictionary containing execution context

    Returns:
        The result of the node execution
    """
    result = node_func(context)
    if inspect.isawaitable(result):
        return await result
    return result