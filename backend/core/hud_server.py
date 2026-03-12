import asyncio
import websockets
import json
import threading

class HUDServer:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = None

    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, message):
        if self.clients:
            data = json.dumps(message)
            await asyncio.gather(*[client.send(data) for client in self.clients])

    async def start_server(self):
        async with websockets.serve(self.register, self.host, self.port):
            print(f"🖥️ HUD Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

    def run_in_thread(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server())

    def start(self):
        t = threading.Thread(target=self.run_in_thread, daemon=True)
        t.start()

    def update_state(self, state, text=""):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast({"state": state, "text": text}),
                self.loop
            )
