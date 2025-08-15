import logging
from common.global_data import gdata


class JM3846ThrustUtil:
    @staticmethod
    def get_avg(data_list, name: str):
        try:
            values_length = len(data_list)
            if values_length == 0:
                return 0

            ch1_sum = 0

            ch_sel_1 = gdata.configSPS.ch_sel_1 if name == 'sps' else gdata.configSPS2.ch_sel_1
            ch_sel_0 = gdata.configSPS.ch_sel_0 if name == 'sps' else gdata.configSPS2.ch_sel_0
            speed_sel = gdata.configSPS.speed_sel if name == 'sps' else gdata.configSPS2.speed_sel
            channel_count = 0
            if ch_sel_1 != 0 and ch_sel_0 != 0 and speed_sel == True:
                channel_count = 3
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch1_sum += chunk[1]

            if ch_sel_1 != 4 and ch_sel_0 != 0 and speed_sel == True:
                channel_count = 2
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch1_sum += chunk[0]

            if ch_sel_1 != 1 and ch_sel_0 != 1 and speed_sel == False:
                channel_count = 2
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch1_sum += chunk[1]

            part_length = values_length / channel_count
            return round(ch1_sum / part_length, 1)

        except:
            logging.exception('exception occured at JM3846Thrust.convert_data')

        return 0
