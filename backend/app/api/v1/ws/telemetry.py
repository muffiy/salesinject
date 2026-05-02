"""
Telemetry WebSocket for Agent OS v2.

Provides real-time operations dashboard telemetry for system monitoring.
"""

import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from app.core.config import settings

router = APIRouter()


@router.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    """
    WebSocket endpoint for operations dashboard telemetry.

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()

    try:
        # Create Kafka consumer for all system events
        consumer = KafkaConsumer(
            "mission:progress",
            "mission:completed",
            "mission:failed",
            "budget:alert",
            "agent:registered",
            "agent:performance",
            "system:health",
            bootstrap_servers=settings.REDPANDA_BROKERS,
            group_id="ws_telemetry",
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000
        )

        try:
            # Send initial system status
            await websocket.send_json({
                "type": "connection_established",
                "message": "Telemetry stream active",
                "topics": [
                    "mission:progress",
                    "mission:completed",
                    "mission:failed",
                    "budget:alert",
                    "agent:registered",
                    "agent:performance",
                    "system:health"
                ]
            })

            # Poll for events
            while True:
                # Check for client ping
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                except asyncio.TimeoutError:
                    pass
                except WebSocketDisconnect:
                    break

                # Poll Kafka
                records = consumer.poll(timeout_ms=1000)
                for topic_partition, messages in records.items():
                    for message in messages:
                        event = message.value

                        # Add telemetry metadata
                        event["_telemetry"] = {
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "timestamp": message.timestamp,
                            "received_at": asyncio.get_event_loop().time()
                        }

                        # Send to WebSocket
                        try:
                            await websocket.send_json(event)
                        except WebSocketDisconnect:
                            break

                # Check for disconnect
                try:
                    await websocket.receive_text()
                except WebSocketDisconnect:
                    break

        except NoBrokersAvailable as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Redpanda not available: {str(e)}"
            })
        finally:
            consumer.close()

    except WebSocketDisconnect:
        # Client disconnected normally
        pass
    except Exception as e:
        # Log error
        print(f"[Telemetry] Error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Telemetry error: {str(e)}"
            })
        except:
            pass


@router.websocket("/ws/telemetry/system")
async def system_telemetry_ws(websocket: WebSocket):
    """
    WebSocket endpoint for detailed system telemetry (admin only).

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()

    try:
        # Create consumer for all topics (including internal ones)
        consumer = KafkaConsumer(
            bootstrap_servers=settings.REDPANDA_BROKERS,
            group_id="ws_system_telemetry",
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000
        )

        # Subscribe to all topics
        consumer.subscribe(pattern=".*")

        try:
            await websocket.send_json({
                "type": "connection_established",
                "message": "System telemetry stream active",
                "scope": "all_topics"
            })

            # Statistics for aggregation
            stats = {
                "messages_received": 0,
                "messages_by_topic": {},
                "last_message_time": None
            }

            # Poll loop
            while True:
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                except asyncio.TimeoutError:
                    pass
                except WebSocketDisconnect:
                    break

                records = consumer.poll(timeout_ms=1000)
                for topic_partition, messages in records.items():
                    for message in messages:
                        topic = message.topic

                        # Update stats
                        stats["messages_received"] += 1
                        stats["messages_by_topic"][topic] = stats["messages_by_topic"].get(topic, 0) + 1
                        stats["last_message_time"] = message.timestamp

                        # Prepare telemetry message
                        telemetry_event = {
                            "type": "system_event",
                            "topic": topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "timestamp": message.timestamp,
                            "value": message.value,
                            "stats": stats.copy()
                        }

                        # Send aggregated stats every 10 messages
                        if stats["messages_received"] % 10 == 0:
                            await websocket.send_json({
                                "type": "system_stats",
                                "stats": stats.copy(),
                                "timestamp": asyncio.get_event_loop().time()
                            })

                        # Send individual event
                        try:
                            await websocket.send_json(telemetry_event)
                        except WebSocketDisconnect:
                            break

                # Send heartbeat every 30 seconds
                await asyncio.sleep(0.1)

                try:
                    await websocket.receive_text()
                except WebSocketDisconnect:
                    break

        except NoBrokersAvailable as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Redpanda not available: {str(e)}"
            })
        finally:
            consumer.close()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[System Telemetry] Error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"System telemetry error: {str(e)}"
            })
        except:
            pass