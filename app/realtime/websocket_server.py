from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Set

app = FastAPI(title="Kova Websocket")
active: Set[WebSocket] = set()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    active.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for peer in list(active):
                try:
                    await peer.send_text(msg)
                except Exception:
                    pass
    except WebSocketDisconnect:
        active.discard(ws)
