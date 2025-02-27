import pytest
from unittest.mock import MagicMock, patch
from src.utils.plc_client import PLCClient


@pytest.fixture
def plc_client():
    # Create an instance of PLCClient with dummy values for testing
    plc_ip = "192.168.0.1"
    rack = 0
    slot = 2
    client = PLCClient(plc_ip, rack, slot)
    yield client
    # Clean up after each test by disconnecting from the PLC
    client.disconnect()


@patch('src.utils.plc_client.snap7.client.Client.connect')
def test_connect(mock_connect, plc_client):
    # Mock the connect method
    mock_connect.return_value = None
    plc_client.plc.get_connected = MagicMock(return_value=True)
    plc_client.connect()
    assert plc_client.plc.get_connected() == True


@patch('src.utils.plc_client.snap7.client.Client.disconnect')
def test_disconnect(mock_disconnect, plc_client):
    # Mock the disconnect method
    mock_disconnect.return_value = None
    plc_client.plc.get_connected = MagicMock(return_value=False)
    plc_client.disconnect()
    assert plc_client.plc.get_connected() == False


@patch('src.utils.plc_client.snap7.client.Client.read_area')
def test_read_data(mock_read_area, plc_client):
    # Mock the read_area method
    mock_read_area.return_value = b'\x00' * 10
    db_number = 1
    start = 0
    size = 10
    data = plc_client.read_data(db_number, start, size)
    assert len(data) == size


def test_parse_data():
    # Test the parse_data method
    client = PLCClient("192.168.0.1", 0, 2)
    data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    parsed_data = client.parse_data(data)
    assert isinstance(parsed_data, tuple)
    assert len(parsed_data) == 2
    assert isinstance(parsed_data[0], float)
    assert isinstance(parsed_data[1], float)
