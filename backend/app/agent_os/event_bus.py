"""
Event Bus for Agent OS v2.

Provides Redpanda (Kafka-compatible) event streaming for mission progress,
agent registration, budget alerts, and other system events.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Callable
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
from ..core.config import settings

logger = logging.getLogger(__name__)

# Global producer instance
_producer: Optional[KafkaProducer] = None


def get_producer() -> KafkaProducer:
    """
    Get or create Kafka producer for Redpanda.

    Returns:
        KafkaProducer instance

    Raises:
        Exception: If unable to connect to Redpanda brokers
    """
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=settings.REDPANDA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Ensure message persistence
                retries=3,   # Retry on failure
                max_block_ms=5000  # Timeout after 5 seconds if brokers unavailable
            )
            logger.info(f"Connected to Redpanda at {settings.REDPANDA_BROKERS}")
        except NoBrokersAvailable as e:
            logger.error(f"No Redpanda brokers available at {settings.REDPANDA_BROKERS}: {e}")
            raise Exception(f"Redpanda connection failed: {e}")
    return _producer


class EventBus:
    """Event bus for publishing and consuming system events."""

    def __init__(self):
        self.producer = get_producer()

    def emit(self, event: str, payload: Dict[str, Any], key: Optional[str] = None) -> bool:
        """
        Emit an event to Redpanda.

        Args:
            event: Event name (topic)
            payload: Event payload dictionary
            key: Optional key for partitioning

        Returns:
            True if event was sent successfully, False otherwise
        """
        try:
            future = self.producer.send(event, key=key, value=payload)
            # Wait for acknowledgement (async in production, sync for simplicity)
            future.get(timeout=10)
            if settings.AGENT_OS_DEBUG:
                logger.debug(f"Emitted event '{event}': {payload}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to emit event '{event}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error emitting event '{event}': {e}")
            return False

    def create_consumer(
        self,
        topics: list,
        group_id: str,
        auto_offset_reset: str = 'earliest'
    ) -> KafkaConsumer:
        """
        Create a Kafka consumer for subscribing to events.

        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            auto_offset_reset: What to do when there's no initial offset

        Returns:
            KafkaConsumer instance
        """
        try:
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=settings.REDPANDA_BROKERS,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                consumer_timeout_ms=10000  # Timeout for polling
            )
            logger.info(f"Created consumer for topics {topics} in group '{group_id}'")
            return consumer
        except Exception as e:
            logger.error(f"Failed to create consumer: {e}")
            raise

    def subscribe(
        self,
        topics: list,
        group_id: str,
        callback: Callable[[Dict[str, Any]], None],
        timeout_ms: int = 1000
    ) -> None:
        """
        Subscribe to topics and process messages with callback.

        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            callback: Function to call with each message value
            timeout_ms: Polling timeout in milliseconds
        """
        consumer = self.create_consumer(topics, group_id)

        try:
            while True:
                records = consumer.poll(timeout_ms=timeout_ms)
                for topic_partition, messages in records.items():
                    for message in messages:
                        try:
                            callback(message.value)
                        except Exception as e:
                            logger.error(f"Error processing message from {topic_partition}: {e}")
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            consumer.close()

    def flush(self) -> None:
        """Flush all pending messages."""
        if self.producer:
            self.producer.flush()


# Common event topics
EVENT_TOPICS = {
    "MISSION_PROGRESS": "mission:progress",
    "BUDGET_ALERT": "budget:alert",
    "AGENT_REGISTERED": "agent:registered",
    "MISSION_COMPLETED": "mission:completed",
    "MISSION_FAILED": "mission:failed",
    "AGENT_PERFORMANCE": "agent:performance",
    "SYSTEM_HEALTH": "system:health",
}


# Utility functions for common event types
def emit_mission_progress(trace_id: str, step: str, status: str, data: Optional[Dict] = None) -> bool:
    """Emit mission progress event."""
    event_bus = EventBus()
    payload = {
        "trace_id": trace_id,
        "step": step,
        "status": status,
        "timestamp": time.time(),
        "data": data or {}
    }
    return event_bus.emit(EVENT_TOPICS["MISSION_PROGRESS"], payload, key=trace_id)


def emit_mission_completed(trace_id: str, result: Dict[str, Any]) -> bool:
    """Emit mission completed event."""
    event_bus = EventBus()
    payload = {
        "trace_id": trace_id,
        "result": result,
        "timestamp": time.time()
    }
    return event_bus.emit(EVENT_TOPICS["MISSION_COMPLETED"], payload, key=trace_id)


def emit_budget_alert(user_id: str, mission_type: str, cost: float, limit: float) -> bool:
    """Emit budget alert event."""
    event_bus = EventBus()
    payload = {
        "user_id": user_id,
        "mission_type": mission_type,
        "cost": cost,
        "limit": limit,
        "timestamp": time.time()
    }
    return event_bus.emit(EVENT_TOPICS["BUDGET_ALERT"], payload, key=user_id)


def emit_agent_performance(agent_name: str, success: bool, duration_ms: float) -> bool:
    """Emit agent performance event."""
    event_bus = EventBus()
    payload = {
        "agent_name": agent_name,
        "success": success,
        "duration_ms": duration_ms,
        "timestamp": time.time()
    }
    return event_bus.emit(EVENT_TOPICS["AGENT_PERFORMANCE"], payload, key=agent_name)