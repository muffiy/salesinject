from __future__ import annotations

import asyncio
from typing import Set
from fastapi import WebSocket


class WSManager:
    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._clients.discard(ws)

    async def broadcast(self, message: str) -> None:
        stale = []
        for ws in self._clients:
            try:
                await ws.send_json({"event": "broadcast", "message": message})
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)

    def broadcast_nowait(self, message: str) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast(message))
        except RuntimeError:
            pass


manager = WSManager()
