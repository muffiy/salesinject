"""
Mission Tracer for Agent OS v2.

Provides detailed mission logging and tracing for observability and replay.
"""

import time
import uuid
import json
from typing import Dict, Any, List, Optional
from ..core.redis_client import r


class WarTracer:
    """Mission tracing and logging with Redis persistence."""

    def start_mission(self, user_id: str, mission_type: str) -> str:
        """
        Start a new mission trace.

        Args:
            user_id: User UUID as string
            mission_type: Type of mission (e.g., "scout", "ammo_generation")

        Returns:
            Trace ID for the mission
        """
        trace_id = str(uuid.uuid4())
        data = {
            "trace_id": trace_id,
            "user_id": user_id,
            "mission_type": mission_type,
            "status": "running",
            "started_at": time.time(),
            "steps": []
        }
        r.setex(f"trace:{trace_id}", 86400, json.dumps(data))  # 24 hours TTL
        self._log(trace_id, f"MISSION STARTED: {mission_type}")
        return trace_id

    def log_step(self, trace_id: str, step: str) -> None:
        """
        Log a step in mission execution.

        Args:
            trace_id: Trace ID of the mission
            step: Step description or data
        """
        self._log(trace_id, step)
        key = f"trace:{trace_id}"
        data_str = r.get(key)
        if data_str:
            data = json.loads(data_str)
            data["steps"] = data.get("steps", []) + [step]
            r.setex(key, 86400, json.dumps(data))

    def finish_mission(self, trace_id: str, result: Dict[str, Any]) -> None:
        """
        Mark a mission as completed with result.

        Args:
            trace_id: Trace ID of the mission
            result: Mission result data
        """
        self._log(trace_id, "MISSION COMPLETED")
        key = f"trace:{trace_id}"
        data_str = r.get(key)
        if data_str:
            data = json.loads(data_str)
            data.update({
                "status": "completed",
                "finished_at": time.time(),
                "result": result
            })
            r.setex(key, 86400, json.dumps(data))

    def fail_mission(self, trace_id: str, error: str) -> None:
        """
        Mark a mission as failed with error.

        Args:
            trace_id: Trace ID of the mission
            error: Error message or stack trace
        """
        self._log(trace_id, f"MISSION FAILED: {error}")
        key = f"trace:{trace_id}"
        data_str = r.get(key)
        if data_str:
            data = json.loads(data_str)
            data.update({
                "status": "failed",
                "error": error,
                "finished_at": time.time()
            })
            r.setex(key, 86400, json.dumps(data))

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace data for a mission.

        Args:
            trace_id: Trace ID of the mission

        Returns:
            Trace data or None if not found
        """
        key = f"trace:{trace_id}"
        data_str = r.get(key)
        if data_str:
            return json.loads(data_str)
        return None

    def get_trace_logs(self, trace_id: str, limit: int = 100) -> List[str]:
        """
        Get raw logs for a mission trace.

        Args:
            trace_id: Trace ID of the mission
            limit: Maximum number of log entries to return

        Returns:
            List of log entries (most recent first)
        """
        key = f"trace_log:{trace_id}"
        logs = r.lrange(key, -limit, -1)
        return logs[::-1] if logs else []  # Reverse to show most recent first

    def _log(self, trace_id: str, message: str) -> None:
        """
        Internal method to log a message to trace log.

        Args:
            trace_id: Trace ID of the mission
            message: Log message
        """
        key = f"trace_log:{trace_id}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_entry = f"[{timestamp}] {message}"
        r.rpush(key, log_entry)
        r.expire(key, 86400)  # 24 hours TTL


# Utility functions for direct tracing access
def start_trace(user_id: str, mission_type: str) -> str:
    """Convenience function to start a trace."""
    tracer = WarTracer()
    return tracer.start_mission(user_id, mission_type)


def log_trace_step(trace_id: str, step: str) -> None:
    """Convenience function to log a trace step."""
    tracer = WarTracer()
    tracer.log_step(trace_id, step)


def finish_trace(trace_id: str, result: Dict[str, Any]) -> None:
    """Convenience function to finish a trace."""
    tracer = WarTracer()
    tracer.finish_mission(trace_id, result)


def fail_trace(trace_id: str, error: str) -> None:
    """Convenience function to fail a trace."""
    tracer = WarTracer()
    tracer.fail_mission(trace_id, error)


def get_recent_traces(user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get recent traces, optionally filtered by user.

    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of traces to return

    Returns:
        List of trace data dictionaries
    """
    tracer = WarTracer()
    pattern = "trace:*"
    trace_keys = r.keys(pattern)

    traces = []
    for key in trace_keys[:limit * 2]:  # Get extra to filter
        data_str = r.get(key)
        if data_str:
            data = json.loads(data_str)
            if user_id and data.get("user_id") != user_id:
                continue
            traces.append(data)

    # Sort by started_at descending (most recent first)
    traces.sort(key=lambda x: x.get("started_at", 0), reverse=True)
    return traces[:limit]