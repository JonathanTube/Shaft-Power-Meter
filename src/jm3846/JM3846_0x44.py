import asyncio
import logging
import struct
from common.global_data import gdata
from jm3846.JM3846_0x45 import JM38460x45
from jm3846.JM3846_util import JM3846Util


class JM38460x44:
    frame_size = 0x0060
    total_frames = 0xFFFF
    running = False
    loop_task: asyncio.Task = None

    @staticmethod
    def build_request(frame_size: int, total_frames: int) -> bytes:
        return struct.pack(
            '>HHHBBHHH',
            0x0004,
            0x0000,
            0x0008,
            0x01,
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
                # 如果Torque调零打开,累计数据
                if gdata.configSPS.zero_cal_torque_running:
                    gdata.configSPS.zero_cal_ad0_for_torque.append(val)

                # 如果thrust调零打开，累计数据
                if gdata.configSPS.zero_cal_thrust_running:
                    gdata.configSPS.zero_cal_ad1_for_thrust.append(val)

                # 没有在调零，才记录
                if not gdata.configSPS.zero_cal_torque_running and not gdata.configSPS.zero_cal_thrust_running:
                    gdata.configSPS.accumulated_data_ad0_ad1_speed.append(val)
                    gdata.configSPS.accumulated_data_ad0_ad1_speed_for_1s.append(val)
                    gdata.configSPS.accumulated_data_ad0_ad1_speed_for_15s.append(val)

            else:
                # 如果Torque调零打开,累计数据
                if gdata.configSPS2.zero_cal_torque_running:
                    gdata.configSPS2.zero_cal_ad0_for_torque.append(val)

                # 如果thrust调零打开，累计数据
                if gdata.configSPS2.zero_cal_thrust_running:
                    gdata.configSPS2.zero_cal_ad1_for_thrust.append(val)

                # 没有在调零，才记录
                if not gdata.configSPS2.zero_cal_torque_running and not gdata.configSPS2.zero_cal_thrust_running:
                    gdata.configSPS2.accumulated_data_ad0_ad1_speed.append(val)
                    gdata.configSPS2.accumulated_data_ad0_ad1_speed_for_1s.append(val)
                    gdata.configSPS2.accumulated_data_ad0_ad1_speed_for_15s.append(val)

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
                    logging.info(f'[JM3846-{name}] 0x44响应请求头为空,重新请求0x44')
                    await asyncio.sleep(1.2)
                    await JM38460x44.send_0x44_again(name, reader, writer)
                    continue
                else:
                    # logging.info(f'[JM3846-{name}] 0x44响应={bytes.hex(frame)}')
                    pass

            except asyncio.TimeoutError:
                logging.warning(f'[JM3846-{name}] 0x44响应 超时')
                continue
            except asyncio.CancelledError:
                await on_error()
                break
            except:
                logging.exception(f'[JM3846-{name}] 0x44响应 error')
                await on_error()
                break

            func_code = struct.unpack(">B", frame[7:8])[0]
            if func_code & 0x80:
                continue

            if func_code == 0x44:
                current_frame = JM38460x44.parse_response(frame, name)
                # logging.info(f'[JM3846-{name}] 0x44响应, 当前帧={current_frame},最大帧={JM38460x44.total_frames}')
                if current_frame + 1 >= JM38460x44.total_frames:
                    logging.info(f'[JM3846-{name}] 0x44响应, 当前帧={current_frame}大于总帧数={JM38460x44.total_frames},重新请求0x44')
                    await JM38460x44.send_0x44_again(name, reader, writer)
                await on_success()

    @staticmethod
    async def send_0x44_again(name, reader, writer):
        # 断开
        await JM38460x45.handle(name, reader, writer)
        # 重新请求
        request = JM38460x44.build_request(JM38460x44.frame_size, JM38460x44.total_frames)
        writer.write(request)
        await writer.drain()

    @staticmethod
    def stop():
        JM38460x44.running = False
        if JM38460x44.loop_task:
            JM38460x44.loop_task.cancel()
