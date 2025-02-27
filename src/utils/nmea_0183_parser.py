import serial
import pynmea2


class NMEAParser:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None

    def connect(self):
        self.serial_connection = serial.Serial(
            self.port, self.baudrate, timeout=1)

    def disconnect(self):
        if self.serial_connection:
            self.serial_connection.close()

    def parse_nmea_sentence(self, sentence):
        try:
            msg = pynmea2.parse(sentence)
            if isinstance(msg, pynmea2.types.talker.RMC):
                utc_date = msg.datestamp
                utc_time = msg.timestamp
                latitude = msg.latitude
                lat_direction = msg.lat_dir
                longitude = msg.longitude
                lon_direction = msg.lon_dir
                return utc_date, utc_time, latitude, lat_direction, longitude, lon_direction
        except pynmea2.ParseError as e:
            print(f"Failed to parse NMEA sentence: {e}")
        return None

    def read_data(self):
        if not self.serial_connection:
            raise Exception(
                "Serial connection not established. Call connect() first.")

        while True:
            line = self.serial_connection.readline().decode('ascii', errors='replace')
            data = self.parse_nmea_sentence(line)
            if data:
                utc_date, utc_time, lat, lat_direction, lon, lon_direction = data
                print(
                    f"UTC Date: {utc_date}, UTC Time: {utc_time}, Latitude: {lat} {lat_direction}, Longitude: {lon} {lon_direction}")
