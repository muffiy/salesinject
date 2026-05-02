"""
Mission Streaming WebSocket for Agent OS v2.

Provides real-time mission progress streaming via Redpanda events.
"""

import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from app.core.config import settings

router = APIRouter()


@router.websocket("/ws/stream/{trace_id}")
async def mission_stream(websocket: WebSocket, trace_id: str):
    """
    WebSocket endpoint for streaming mission progress events.

    Args:
        websocket: WebSocket connection
        trace_id: Mission trace ID to stream events for
    """
    await websocket.accept()

    try:
        # Create Kafka consumer for mission progress events
        consumer = KafkaConsumer(
            "mission:progress",
            "mission:completed",
            "mission:failed",
            bootstrap_servers=settings.REDPANDA_BROKERS,
            group_id=f"ws_stream_{trace_id}",
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000
        )

        try:
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "connection_established",
                "trace_id": trace_id,
                "message": "Streaming mission events"
            })

            # Poll for events
            while True:
                # Check if WebSocket is still connected
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    # Client sent a message, ignore for now (could be ping)
                except asyncio.TimeoutError:
                    # No message from client, continue polling
                    pass
                except WebSocketDisconnect:
                    break

                # Poll Kafka for messages
                records = consumer.poll(timeout_ms=1000)
                for topic_partition, messages in records.items():
                    for message in messages:
                        event = message.value

                        # Filter by trace_id
                        if event.get("trace_id") == trace_id:
                            # Add metadata
                            event["_meta"] = {
                                "topic": message.topic,
                                "partition": message.partition,
                                "offset": message.offset,
                                "timestamp": message.timestamp
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
        print(f"[Mission Stream] Error for trace {trace_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Stream error: {str(e)}"
            })
        except:
            pass


@router.websocket("/ws/stream/user/{user_id}")
async def user_missions_stream(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for streaming all missions for a user.

    Args:
        websocket: WebSocket connection
        user_id: User ID to stream events for
    """
    await websocket.accept()

    try:
        # Create Kafka consumer for user events
        consumer = KafkaConsumer(
            "mission:progress",
            "mission:completed",
            "mission:failed",
            "budget:alert",
            bootstrap_servers=settings.REDPANDA_BROKERS,
            group_id=f"ws_user_{user_id}",
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000
        )

        try:
            await websocket.send_json({
                "type": "connection_established",
                "user_id": user_id,
                "message": "Streaming user mission events"
            })

            # Poll for events
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
                        event = message.value

                        # Filter by user_id
                        if event.get("user_id") == user_id:
                            event["_meta"] = {
                                "topic": message.topic,
                                "timestamp": message.timestamp
                            }

                            try:
                                await websocket.send_json(event)
                            except WebSocketDisconnect:
                                break

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
        print(f"[User Mission Stream] Error for user {user_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Stream error: {str(e)}"
            })
        except:
            pass