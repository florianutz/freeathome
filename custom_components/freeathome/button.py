"""Support for free@home trigger buttons."""

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up free@home trigger buttons."""
    sysap = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [FreeAtHomeTriggerButton(device) for device in sysap.get_devices("button")]
        + [FreeAtHomeDoorOpenerButton(device) for device in sysap.get_devices("lock")]
    )


class FreeAtHomeTriggerButton(ButtonEntity):
    """Represent a momentary free@home trigger."""

    _attr_should_poll = False

    def __init__(self, device):
        """Initialize the trigger button."""
        self.trigger_device = device
        self._attr_name = device.name

    @property
    def device_info(self):
        """Return device information."""
        return self.trigger_device.device_info

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self.trigger_device.unique_id

    async def async_press(self):
        """Send one timed trigger pulse."""
        await self.trigger_device.press()


class FreeAtHomeDoorOpenerButton(FreeAtHomeTriggerButton):
    """Represent a free@home door opener button."""

    _attr_icon = "mdi:door-open"

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"{self.trigger_device.unique_id}_door_opener"

    async def async_press(self):
        """Trigger the door opener."""
        await self.trigger_device.unlock()
