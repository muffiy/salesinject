"""
War Engine for Agent OS v2.

Main orchestrator for mission execution with pre-flight checks, budget management,
concurrency limits, and comprehensive tracing.
"""

import json
from typing import Any, Dict, Optional
from .engine_v2 import WorkflowEngineV2
from .tracer import WarTracer
from .missions import get_mission_nodes
from .concurrency import check_concurrency, increment_active, decrement_active
from .budget import check_budget
from .cost_engine import check_mission_cost
from ..core.redis_client import r
from ..services.memory_service import get_or_create_session, save_memory


class WarEngine:
    """Main mission orchestrator with full lifecycle management."""

    def __init__(self):
        self.engine = WorkflowEngineV2()
        self.tracer = WarTracer()

    async def launch_mission(
        self,
        mission_type: str,
        user_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Launch a mission with full pre-flight checks and lifecycle management.

        Args:
            mission_type: Type of mission (e.g., "scout", "ammo_generation")
            user_id: User UUID as string
            payload: Mission-specific payload

        Returns:
            Mission result dictionary

        Raises:
            Exception: If pre-flight checks fail
        """
        # Pre-flight checks
        check_concurrency(user_id)
        check_budget(user_id)
        check_mission_cost(user_id, mission_type, 0.05)  # Estimated cost

        # Reserve slot
        increment_active(user_id)

        # Get workflow for mission
        workflow = get_mission_nodes(mission_type)

        # Create session for memory isolation
        session_id = get_or_create_session(user_id, f"war:{mission_type}")

        # Start mission trace
        trace_id = self.tracer.start_mission(user_id, mission_type)

        # Build execution context
        context = {
            "user_id": user_id,
            "session_id": session_id,
            "trace_id": trace_id,
            "mission_type": mission_type,
            "payload": payload,
            "step_results": {}
        }

        # Store replay data
        r.setex(
            f"mission:replay:{trace_id}",
            86400,  # 24 hours
            json.dumps(context)
        )

        try:
            # Execute workflow
            result = await self.engine.execute(workflow, context)

            # Mission completed successfully
            self.tracer.finish_mission(trace_id, result)

            # Save to memory
            save_memory(
                user_id=user_id,
                session_id=session_id,
                agent_type="war_engine",
                memory_type="mission_result",
                content=result
            )

            return {
                "status": "success",
                "trace_id": trace_id,
                "session_id": session_id,
                "result": result,
                "workflow": workflow
            }

        except Exception as e:
            # Mission failed
            error_str = str(e)
            self.tracer.fail_mission(trace_id, error_str)

            # Save error to memory
            save_memory(
                user_id=user_id,
                session_id=session_id,
                agent_type="war_engine",
                memory_type="mission_error",
                content={"error": error_str, "payload": payload}
            )

            raise

        finally:
            # Release concurrency slot
            decrement_active(user_id)

    async def launch_mission_with_fallback(
        self,
        mission_type: str,
        user_id: str,
        payload: Dict[str, Any],
        fallback_mission: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Launch mission with fallback option.

        Args:
            mission_type: Primary mission type
            user_id: User UUID as string
            payload: Mission payload
            fallback_mission: Optional fallback mission type

        Returns:
            Mission result or fallback result
        """
        try:
            return await self.launch_mission(mission_type, user_id, payload)
        except Exception as primary_error:
            if not fallback_mission:
                raise

            self.tracer.log_step(
                "fallback_init",
                f"Primary mission '{mission_type}' failed, trying fallback '{fallback_mission}': {primary_error}"
            )

            try:
                return await self.launch_mission(fallback_mission, user_id, payload)
            except Exception as fallback_error:
                raise Exception(
                    f"Both primary and fallback missions failed: "
                    f"Primary: {primary_error}, Fallback: {fallback_error}"
                )

    def get_mission_status(self, trace_id: str) -> Dict[str, Any]:
        """
        Get status of a mission.

        Args:
            trace_id: Trace ID of the mission

        Returns:
            Mission status information
        """
        return self.engine.get_workflow_status(trace_id)

    def get_mission_replay(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get replay data for a mission.

        Args:
            trace_id: Trace ID of the mission

        Returns:
            Replay data or None if not found
        """
        key = f"mission:replay:{trace_id}"
        data = r.get(key)
        if data:
            return json.loads(data)
        return None

    def list_user_missions(
        self,
        user_id: str,
        limit: int = 20,
        mission_type: Optional[str] = None
    ) -> list:
        """
        List missions for a user.

        Args:
            user_id: User UUID as string
            limit: Maximum number of missions to return
            mission_type: Optional filter by mission type

        Returns:
            List of mission summaries
        """
        # Get recent traces for user
        traces = self.tracer.get_recent_traces(user_id, limit * 2)

        results = []
        for trace in traces:
            if mission_type and trace.get("mission_type") != mission_type:
                continue

            results.append({
                "trace_id": trace.get("trace_id"),
                "mission_type": trace.get("mission_type"),
                "status": trace.get("status"),
                "started_at": trace.get("started_at"),
                "finished_at": trace.get("finished_at"),
                "error": trace.get("error"),
                "steps_count": len(trace.get("steps", []))
            })

            if len(results) >= limit:
                break

        return results

    def cancel_mission(self, trace_id: str, user_id: str) -> bool:
        """
        Cancel a running mission.

        Args:
            trace_id: Trace ID of the mission
            user_id: User UUID as string

        Returns:
            True if cancelled, False if not found or not running
        """
        # Check if mission belongs to user
        trace = self.tracer.get_trace(trace_id)
        if not trace or trace.get("user_id") != user_id:
            return False

        # Check if mission is still running
        if trace.get("status") != "running":
            return False

        # Mark as cancelled
        self.tracer.fail_mission(trace_id, "Cancelled by user")

        # Release concurrency slot if still active
        # Note: This assumes the mission hasn't already released it
        decrement_active(user_id)

        return True