"""Support for Free@Home door opener buttons."""
import logging

try:
    from homeassistant.components.button import ButtonEntity
except ImportError:
    class ButtonEntity:
        """Fallback for testing without homeassistant package."""
        pass

try:
    from .const import DOMAIN
except ImportError:
    from const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices, discovery_info=None):
    """Set up the Free@Home door opener button platform."""
    _LOGGER.info("FreeAtHome setup button")

    fah = hass.data[DOMAIN][config_entry.entry_id]

    devices = fah.get_devices("lock")

    for device_object in devices:
        async_add_devices([FreeAtHomeDoorOpenerButton(device_object)])


class FreeAtHomeDoorOpenerButton(ButtonEntity):
    """Representation of a Free@Home door opener trigger button."""

    _attr_icon = "mdi:door-open"

    def __init__(self, device):
        """Initialize the button."""
        self._device = device
        self._name = device.name

    @property
    def name(self):
        """Return the display name of the button."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.serialnumber}/{self._device.channel_id}_door_opener"

    @property
    def device_info(self):
        """Return device id."""
        return self._device.device_info

    @property
    def should_poll(self):
        """Return that polling is not necessary."""
        return False

    async def async_added_to_hass(self):
        """Register callback to update hass after device was changed."""
        async def after_update_callback(device):
            """Call after device was updated."""
            await self.async_update_ha_state(True)

        self._device.register_device_updated_cb(after_update_callback)

    async def async_press(self) -> None:
        """Trigger door opener via service call or UI click."""
        await self._device.open()
