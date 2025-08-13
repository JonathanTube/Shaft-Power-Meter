import asyncio
import logging
import struct
from common.global_data import gdata
from jm3846.JM3846_torque_rpm import jm3846_torque_rpm
from jm3846.JM3846_thrust import jm3846_thrust
from jm3846.JM3846_util import JM3846Util


class JM38460x44:
    frame_size = 120
    total_frames = 0xFFFF
    running = False
    loop_task: asyncio.Task = None

    @staticmethod
    def build_request(frame_size: int, total_frames: int) -> bytes:
        return struct.pack(
            '>HHHBBHHH',
            0x0044,
            0x0000,
            8,
            0xFF,
            0x44,
            0x0000,
            frame_size,
            total_frames
        )

    @staticmethod
    def parse_response(data: bytes, name: str) -> int:
        _, _, length, _ = struct.unpack(">HHHB", data[:7])
        current_frame = struct.unpack('>H', data[8:10])[0]
        payload_length = length - 5
        payload_start = 12
        payload_end = payload_start + payload_length
        payload = data[payload_start: payload_end]

        for i in range(0, len(payload), 2):
            if i + 1 >= len(payload):
                break
            val = struct.unpack('<H', payload[i:i+2])[0]

            if name == 'sps':
                if gdata.configSPS.zero_cal_torque_running:
                    gdata.configSPS.zero_cal_ad0_for_torque.append(val)
                else:
                    jm3846_torque_rpm.accumulated_data.append(val)

                if gdata.configSPS.zero_cal_thrust_running:
                    gdata.configSPS.zero_cal_ad1_for_thrust.append(val)
                else:
                    jm3846_thrust.accumulated_data.append(val)
            else:
                if gdata.configSPS2.zero_cal_torque_running:
                    gdata.configSPS2.zero_cal_ad0_for_torque.append(val)
                else:
                    jm3846_torque_rpm.accumulated_data.append(val)

                if gdata.configSPS2.zero_cal_thrust_running:
                    gdata.configSPS2.zero_cal_ad1_for_thrust.append(val)
                else:
                    jm3846_thrust.accumulated_data.append(val)

        return current_frame

    @staticmethod
    async def handle(name, reader, writer, on_success: callable, on_error: callable):
        if writer is None or writer.is_closing():
            logging.warning(f"[{name}] connection closed, stopping handle")
            return

        request = JM38460x44.build_request(JM38460x44.frame_size, JM38460x44.total_frames)
        logging.info(f'[JM3846-{name}] send 0x44 req hex={bytes.hex(request)}')

        try:
            writer.write(request)
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError) as e:
            logging.error(f"[{name}] connection error: {e}")
        except Exception:
            logging.exception(f"[{name}] unexpected error in drain")

        JM38460x44.running = True
        JM38460x44.loop_task = asyncio.create_task(JM38460x44.receive_0x44(name, reader, writer, on_success, on_error))
        await JM38460x44.loop_task

    @staticmethod
    async def receive_0x44(name, reader, writer, on_success: callable, on_error: callable):
        while JM38460x44.running:
            try:
                frame = await JM3846Util.read_frame(reader)
                if frame is None:
                    logging.info(f'[JM3846-{name}] receive_0x44 当前frame为空,跳过')
                    continue

            except asyncio.TimeoutError:
                logging.warning(f'[JM3846-{name}] receive_0x44 超时')
            except asyncio.CancelledError:
                on_error()
                break
            except:
                logging.exception(f'[JM3846-{name}] receive_0x44 error')
                on_error()
                break

            func_code = struct.unpack(">B", frame[7:8])[0]
            if func_code & 0x80:
                continue

            if func_code == 0x44:
                current_frame = JM38460x44.parse_response(frame, name)
                if current_frame + 1 >= JM38460x44.total_frames:
                    request = JM38460x44.build_request(JM38460x44.frame_size, JM38460x44.total_frames)
                    logging.info(f'[JM3846-{name}] send 0x44 req (current_frame={current_frame}) is greater than (total_frames={JM38460x44.total_frames})')
                    writer.write(request)
                    await writer.drain()
                on_success()

    @staticmethod
    def stop():
        JM38460x44.running = False
        if JM38460x44.loop_task:
            JM38460x44.loop_task.cancel()
