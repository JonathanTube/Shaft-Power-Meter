import asyncio
import websockets
from typing import Callable, Set
import logging
from db.models.io_conf import IOConf
import msgpack

# ====================== 服务端类 ======================


class WebSocketServer:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.message_handler: Callable = None

    def set_message_handler(self, handler: Callable):
        """设置消息处理回调函数"""
        self.message_handler = handler

    async def _client_handler(self, websocket):
        """处理客户端连接"""
        self.clients.add(websocket)
        logging.info(f"客户端 {websocket.remote_address} 已连接")

        try:
            async for data in websocket:
                # 解包二进制数据
                print(f"服务端收到: {data}")

                # 调用自定义消息处理器
                if self.message_handler:
                    response = self.message_handler(data)
                    if response:
                        await self.send_to_client(websocket, response)
        except websockets.ConnectionClosed:
            logging.error(f"客户端 {websocket.remote_address} 断开连接")
        finally:
            self.clients.remove(websocket)

    async def start(self):
        """启动服务端"""
        host = '0.0.0.0'

        io_conf: IOConf = IOConf.get()
        port = io_conf.hmi_server_port
        try:
            self.server = await websockets.serve(self._client_handler, host, port)
            logging.info(f"服务端已启动 ws://{host}:{port}")
        except Exception:
            return False

        return True

    async def send_to_client(self, client, data):
        """向指定客户端发送数据"""
        packed_data = msgpack.packb(data)
        if client in self.clients:
            await client.send(packed_data)
            return True
        return False

    async def broadcast(self, data):
        """向所有客户端广播数据"""
        logging.info(f"向所有客户端广播数据: {data}")
        if not self.clients:
            return False
        packed_data = msgpack.packb(data)
        await asyncio.gather(
            *[client.send(packed_data) for client in self.clients]
        )
        return True

    async def stop(self):
        """停止服务端"""
        try:
            if self.server:
                self.server.close()
                await self.server.wait_closed()
        except Exception:
            return False

        return True

ws_server = WebSocketServer()
# # 服务端消息处理器
# def server_message_handler(data):
#     print(f"服务端处理消息: {data}")

#     # 主动向客户端发送响应
#     return "已处理"


# async def main_server():
#     server = WebSocketServer(port=8765)
#     server.set_message_handler(server_message_handler)
#     await server.start()

#     # 服务端主动广播消息（每5秒一次）
#     while True:
#         await server.broadcast('hello world 22222')
#         await asyncio.sleep(5)

# # 启动服务端
# asyncio.run(main_server())
