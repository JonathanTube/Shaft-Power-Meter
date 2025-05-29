from db.models.io_conf import IOConf
from jm3846.JM3846_client import JM3846AsyncClient


class Sps2ReadTask(JM3846AsyncClient):
    def __init__(self):
        self.name = 'sps2'

    def get_ip_port(self) -> tuple[str, int]:
        io_conf: IOConf = IOConf.get()
        host = io_conf.sps2_ip
        port = io_conf.sps2_port
        return [host, port]
