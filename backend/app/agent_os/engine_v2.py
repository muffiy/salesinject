"""
Workflow Engine V2 for Agent OS v2.

Distributed, fault-tolerant workflow execution with retry, fallback, and partial results.
Uses Celery for distributed task execution with node routing to specialized queues.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from celery import current_app
from celery.result import AsyncResult

from .router import get_queue_for_node
from .tracer import WarTracer
from .event_bus import EventBus, emit_mission_progress
from .market import get_best_agent, record_agent_performance
from .runtime import run_async_safe


class WorkflowEngineV2:
    """Distributed workflow engine with fault tolerance."""

    def __init__(self):
        self.bus = EventBus()
        self.tracer = WarTracer()

    async def execute(self, workflow: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow sequence with retry and fallback mechanisms.

        Args:
            workflow: List of node names in execution order
            context: Execution context passed to each node

        Returns:
            Dictionary of node results
        """
        results: Dict[str, Any] = {}
        context["step_results"] = results  # Make results available to nodes

        for node_name in workflow:
            start_time = time.time()
            node_result = None
            error = None

            # Try primary node with retries
            for retry in range(3):
                try:
                    self.tracer.log_step(
                        context["trace_id"],
                        f"Executing node '{node_name}' (attempt {retry + 1}/3)"
                    )

                    # Get queue for node
                    queue = get_queue_for_node(node_name)

                    # Send Celery task
                    task = current_app.send_task(
                        f"app.agent_os.nodes.{node_name}",
                        args=[context],
                        queue=queue
                    )

                    # Wait for result (async polling)
                    node_result = await self._wait_for_task(task, node_name, context["trace_id"])

                    # Record success
                    duration_ms = (time.time() - start_time) * 1000
                    record_agent_performance(node_name, True, duration_ms, context.get("user_id"))

                    results[node_name] = node_result
                    context["step_results"][node_name] = node_result

                    # Emit progress event
                    emit_mission_progress(
                        context["trace_id"],
                        node_name,
                        "completed",
                        {"duration_ms": duration_ms, "retries": retry}
                    )

                    self.tracer.log_step(context["trace_id"], f"NODE {node_name} OK")
                    break  # Success, exit retry loop

                except Exception as e:
                    error = str(e)
                    duration_ms = (time.time() - start_time) * 1000
                    record_agent_performance(node_name, False, duration_ms, context.get("user_id"))

                    if retry < 2:  # Not last retry
                        wait_time = 2 ** retry  # Exponential backoff: 1s, 2s, 4s
                        self.tracer.log_step(
                            context["trace_id"],
                            f"Node '{node_name}' failed, retrying in {wait_time}s: {error}"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        # Last retry failed, try fallback
                        self.tracer.log_step(
                            context["trace_id"],
                            f"Node '{node_name}' failed after 3 attempts, trying fallback: {error}"
                        )

                        # Try fallback agent
                        fallback_node = get_best_agent([f"{node_name}_alt", f"fallback_{node_name}"])
                        if fallback_node and fallback_node != node_name:
                            self.tracer.log_step(
                                context["trace_id"],
                                f"Falling back to alternative agent: {fallback_node}"
                            )
                            # Reset for fallback attempt
                            node_name = fallback_node
                            retry = -1  # Reset retry counter
                            continue

                        # No fallback available, record failure
                        results[node_name] = {"error": error, "status": "failed"}
                        context["step_results"][node_name] = results[node_name]

                        emit_mission_progress(
                            context["trace_id"],
                            node_name,
                            "failed",
                            {"error": error, "duration_ms": duration_ms}
                        )

                        # Continue workflow with partial results
                        self.tracer.log_step(
                            context["trace_id"],
                            f"NODE {node_name} FAILED, continuing workflow with partial results"
                        )
                        break

        return results

    async def _wait_for_task(self, task: AsyncResult, node_name: str, trace_id: str) -> Any:
        """
        Wait for Celery task completion with progress updates.

        Args:
            task: Celery AsyncResult
            node_name: Name of the node for logging
            trace_id: Trace ID for progress events

        Returns:
            Task result

        Raises:
            Exception: If task fails
        """
        # Poll for completion
        while not task.ready():
            await asyncio.sleep(0.5)
            # Update progress
            emit_mission_progress(
                trace_id,
                node_name,
                "running",
                {"task_id": task.id, "state": task.state}
            )

        if task.successful():
            return task.result
        else:
            error = str(task.result) if task.result else "Unknown error"
            raise Exception(f"Task {node_name} failed: {error}")

    async def execute_with_timeout(
        self,
        workflow: List[str],
        context: Dict[str, Any],
        timeout_seconds: float = 300
    ) -> Dict[str, Any]:
        """
        Execute workflow with overall timeout.

        Args:
            workflow: List of node names
            context: Execution context
            timeout_seconds: Overall timeout in seconds

        Returns:
            Dictionary of node results

        Raises:
            asyncio.TimeoutError: If workflow exceeds timeout
        """
        try:
            return await asyncio.wait_for(
                self.execute(workflow, context),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            self.tracer.log_step(
                context["trace_id"],
                f"Workflow timeout after {timeout_seconds}s"
            )
            raise

    def execute_sync(self, workflow: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous version of execute for use in Celery tasks.

        Args:
            workflow: List of node names
            context: Execution context

        Returns:
            Dictionary of node results
        """
        return run_async_safe(self.execute, workflow, context)

    def get_workflow_status(self, trace_id: str) -> Dict[str, Any]:
        """
        Get current status of a workflow execution.

        Args:
            trace_id: Trace ID of the workflow

        Returns:
            Status information
        """
        trace = self.tracer.get_trace(trace_id)
        if not trace:
            return {"status": "unknown", "trace_id": trace_id}

        # Count completed vs total nodes
        steps = trace.get("steps", [])
        completed = sum(1 for step in steps if "OK" in step or "COMPLETED" in step)
        failed = sum(1 for step in steps if "FAILED" in step)

        return {
            "trace_id": trace_id,
            "status": trace.get("status", "unknown"),
            "mission_type": trace.get("mission_type", "unknown"),
            "user_id": trace.get("user_id"),
            "started_at": trace.get("started_at"),
            "progress": {
                "completed": completed,
                "failed": failed,
                "total": len(steps),
                "percentage": (completed / len(steps)) * 100 if steps else 0
            },
            "last_error": trace.get("error"),
            "result": trace.get("result")
        }