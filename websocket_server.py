import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)

class AvatarServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connected_clients = set()

    async def register(self, websocket):
        self.connected_clients.add(websocket)
        logging.info("Avatar bağlandı.")

    async def unregister(self, websocket):
        self.connected_clients.remove(websocket)
        logging.info("Avatar bağlantısı kesildi.")

    async def send_state(self, emotion: str, viseme_data: str, audio_url: str):
        if not self.connected_clients:
            return
        payload = json.dumps({
            "emotion": emotion,
            "visemes": viseme_data,
            "audio_url": audio_url
        })
        await asyncio.gather(*[client.send(payload) for client in self.connected_clients])

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                logging.info(f"Avatardan gelen veri: {message}")
        except websockets.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def start(self):
        return await websockets.serve(self.handler, self.host, self.port)
