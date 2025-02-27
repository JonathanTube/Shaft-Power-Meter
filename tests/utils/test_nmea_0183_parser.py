import pytest
from src.utils.nmea_0183_parser import NMEAParser
from datetime import date, time, timezone


@pytest.fixture
def parser():
    return NMEAParser('COM1', 4800)


def test_connect(mocker, parser):
    mock_serial = mocker.patch('serial.Serial')
    parser.connect()
    mock_serial.assert_called_once_with('COM1', 4800, timeout=1)
    assert parser.serial_connection is not None


def test_disconnect(mocker, parser):
    mock_serial = mocker.patch('serial.Serial')
    parser.connect()
    parser.disconnect()
    parser.serial_connection.close.assert_called_once()


def test_parse_nmea_sentence(parser):
    sentence = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
    result = parser.parse_nmea_sentence(sentence)
    expected_date = date(1994, 3, 23)
    expected_time = time(12, 35, 19, tzinfo=timezone.utc)

    assert result == (expected_date, expected_time,
                      48.1173, 'N', 11.516666666666667, 'E')


def test_read_data(mocker, parser):
    mock_serial = mocker.patch('serial.Serial')
    mock_serial_instance = mock_serial.return_value
    mock_serial_instance.readline.side_effect = [
        b"$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A\r\n",
        KeyboardInterrupt
    ]

    parser.connect()
    with pytest.raises(KeyboardInterrupt):
        parser.read_data()

    mock_serial_instance.readline.assert_called()
