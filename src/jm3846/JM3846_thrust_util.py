import logging
from common.global_data import gdata


class JM3846ThrustUtil:
    @staticmethod
    def get_avg(data_list):
        try:
            values_length = len(data_list)
            if values_length == 0:
                return 0

            ch1_sum = 0

            if gdata.ch_sel_1 != 0 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
                channel_count = 3
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    ch1_sum += chunk[1]

                return ch1_sum / part_length

            if gdata.ch_sel_1 != 4 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    ch1_sum += chunk[0]

                return ch1_sum / part_length

            if gdata.ch_sel_1 != 1 and gdata.ch_sel_0 != 1 and gdata.speed_sel == 0:
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = data_list[i: i + channel_count]
                    ch1_sum += chunk[1]

                return ch1_sum / part_length

        except:
            logging.exception('exception occured at JM3846Thrust.convert_data')

        return 0
