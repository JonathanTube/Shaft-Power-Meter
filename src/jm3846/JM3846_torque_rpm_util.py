import logging
from common.global_data import gdata

class JM3846TorqueRpmUtil:
    @staticmethod
    def get_avg(data_list, name:str) -> tuple[float, float]:
        try:
            values_length = len(data_list)
            if values_length == 0:
                return (0, 0)

            # CH_SEL1\CH_SEL0 都不为0且SPEED_SEL=1时：ch0-ch1-rpm-ch0-ch1-rpm-；
            # CH_SEL1\CH_SEL0 都不为4\0且SPEED_SEL=1时： ch1-rpm -ch1-rpm-;
            # CH_SEL1\CH_SEL0 都不为0\1且SPEED_SEL=1时： ch0-rpm -ch0-rpm-;
            # CH_SEL1\CH_SEL0 都不为1\1且SPEED_SEL=0时： ch0-ch1 -ch0-ch1-；
            ch0_sum = 0
            rpm_sum = 0
            ch_sel_1 = gdata.configSPS.ch_sel_1 if name == 'sps' else gdata.configSPS2.ch_sel_1
            ch_sel_0 = gdata.configSPS.ch_sel_0 if name == 'sps' else gdata.configSPS2.ch_sel_0
            speed_sel = gdata.configSPS.speed_sel if name == 'sps' else gdata.configSPS2.speed_sel
            if ch_sel_1 != 0 and ch_sel_0 != 0 and speed_sel == 1:
                ch0_sum = 0
                rpm_sum = 0
                channel_count = 3
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch0_sum += chunk[0]
                        rpm_sum += chunk[2]

            elif ch_sel_1 != 4 and ch_sel_0 != 0 and speed_sel == 1:
                rpm_sum = 0
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    if len(chunk) == channel_count:
                        rpm_sum += chunk[1]

            elif ch_sel_1 != 0 and ch_sel_0 != 1 and speed_sel == 1:
                ch0_sum = 0
                rpm_sum = 0
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch0_sum += chunk[0]
                        rpm_sum += chunk[1]

            elif ch_sel_1 != 1 and ch_sel_0 != 1 and speed_sel == 0:
                ch0_sum = 0
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch0_sum += chunk[0]

            ch0_ad = ch0_sum / part_length if ch0_sum else 0
            rpm = rpm_sum / part_length if rpm_sum else 0

            return (ch0_ad, rpm)
        except:
            logging.exception('exception occured at JM3846TorqueRpm.convert_data')

        return (0, 0)
