from db.models.io_conf import IOConf
from jm3846.JM3846_client import JM3846AsyncClient


class Sps1ReadTask(JM3846AsyncClient):
    def __init__(self):
        super().__init__('sps1')

    def get_ip_port(self) -> tuple[str, int]:
        io_conf: IOConf = IOConf.get()
        host = io_conf.sps1_ip
        port = io_conf.sps1_port
        return [host, port]

