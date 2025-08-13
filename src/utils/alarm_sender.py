from common.global_data import gdata
from db.models.alarm_log import AlarmLog
from websocket.websocket_master import ws_server


class AlarmSender:
    @staticmethod
    async def send_alarms_to_slave():

        if not gdata.configCommon.is_master:
            return

        # 查找未同步的数据
        alarms: list[AlarmLog] = AlarmLog.select(
            AlarmLog.alarm_type,
            AlarmLog.occured_time,
            AlarmLog.recovery_time,
            AlarmLog.acknowledge_time
        ).where(
            AlarmLog.out_of_sync == False,
            AlarmLog.is_synced == False
        ).limit(100)

        arr = []
        for alarm in alarms:
            arr.append({
                'alarm_uuid': alarm.alarm_uuid,
                'alarm_type': alarm.alarm_type,
                'occured_time': gdata.configDateTime.utc,
                'out_of_sync': True
            })

        await ws_server.send({
            'type': 'alarms',
            'data': arr
        })
