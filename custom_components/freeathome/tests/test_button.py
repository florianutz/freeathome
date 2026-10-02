import pytest
pytestmark = pytest.mark.asyncio

import os
import logging
from async_mock import patch, AsyncMock

from fah.pfreeathome import Client
from common import load_fixture, init_client_state
from button import FreeAtHomeDoorOpenerButton
from lock import FreeAtHomeLock

LOG = logging.getLogger(__name__)


def get_client():
    client = Client()
    client.set_datapoint = AsyncMock()
    client._host = "localhost"
    client.component_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    return client


@pytest.fixture(autouse=True)
def mock_init():
    with patch("fah.pfreeathome.Client.__init__", init_client_state):
        yield


@pytest.fixture(autouse=True)
def mock_roomnames():
    with patch("fah.pfreeathome.get_room_names", return_value={"00": {"00": "room1", "01": "room2"}}):
        yield


@patch("fah.pfreeathome.Client.get_config", return_value=load_fixture("panel_door_opener.xml"))
class TestDoorOpenerButton:
    async def test_door_opener_buttons(self, _):
        client = get_client()
        await client.find_devices(True)

        devices = client.get_devices("lock")
        # ch0010 and ch0014 should be discovered, ch0011 (pairingId=FFFF) ignored
        assert len(devices) == 2

        # ch0010: explicit displayName "Main door opener"
        device_10 = next((el for el in devices if el.lookup_key == "ABB600012345/ch0010"))
        assert device_10.name == "Main door opener (room1)"
        assert device_10.serialnumber == "ABB600012345"
        assert device_10.channel_id == "ch0010"

        # ch0014: no displayName, resolved via names.json "007E" -> "Voreingestellte Tür"
        device_14 = next((el for el in devices if el.lookup_key == "ABB600012345/ch0014"))
        assert device_14.name == "Voreingestellte Tür (room1)"
        assert device_14.serialnumber == "ABB600012345"
        assert device_14.channel_id == "ch0014"

        # Test button entity for ch0010
        btn_10 = FreeAtHomeDoorOpenerButton(device_10)
        assert btn_10.name == "Main door opener (room1)"
        assert btn_10.unique_id == "ABB600012345/ch0010_door_opener"
        assert btn_10.device_info == device_10.device_info
        assert btn_10.should_poll is False

        # Pressing button triggers '1' on idp0000
        await btn_10.async_press()
        client.set_datapoint.assert_called_once_with("ABB600012345", "ch0010", "idp0000", "1")

        # Test button entity for ch0014 (Default door)
        client.set_datapoint.reset_mock()
        btn_14 = FreeAtHomeDoorOpenerButton(device_14)
        assert btn_14.name == "Voreingestellte Tür (room1)"
        assert btn_14.unique_id == "ABB600012345/ch0014_door_opener"

        await btn_14.async_press()
        client.set_datapoint.assert_called_once_with("ABB600012345", "ch0014", "idp0000", "1")

        # Also verify FreeAtHomeLock async_open
        client.set_datapoint.reset_mock()
        lock_10 = FreeAtHomeLock(device_10)
        assert lock_10.supported_features == 1
        await lock_10.async_open()
        client.set_datapoint.assert_called_once_with("ABB600012345", "ch0010", "idp0000", "1")

    async def test_door_opener_buttons_no_room_name(self, _):
        client = get_client()
        await client.find_devices(False)

        devices = client.get_devices("lock")
        assert len(devices) == 2

        device_10 = next((el for el in devices if el.lookup_key == "ABB600012345/ch0010"))
        assert device_10.name == "Main door opener"

        device_14 = next((el for el in devices if el.lookup_key == "ABB600012345/ch0014"))
        assert device_14.name == "Voreingestellte Tür"
