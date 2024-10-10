# import socket
import asyncio

class User:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, player_id=None) -> None:
        self.player_id: str | None = player_id
        # self.socket: socket.socket = sock
        self.writer: asyncio.StreamWriter = writer
        self.reader: asyncio.StreamReader = reader
        # self.addr = addr

    def start_using_player(self, unique_name: str) -> None:
        self.player_id = unique_name

    async def send_message(self, msg: str):
        self.writer.write(msg.encode('utf8'))
        await self.writer.drain()

    async def receive_message(self):
        try:
            return (await self.reader.read(1024)).decode()
        
        except Exception as e:
            print(f"Error receiving message for {self.player_id}:", e)
            return None


        # except asyncio.CancelledError:
        #     print(f"Message successfully cancelled for {self.player_id}")
        #     raise asyncio.CancelledError