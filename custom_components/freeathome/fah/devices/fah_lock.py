import asyncio
import logging

from .fah_device import FahDevice
from ..const import (
        FUNCTION_IDS_DOOR_OPENER,
        PID_TIMED_START_STOP,
        PID_INFO_ON_OFF,
    )

LOG = logging.getLogger(__name__)

class FahLock(FahDevice):
    """Free@home lock control via 7 inch panel"""
    state = None

    def pairing_ids(function_id=None):
        if function_id in FUNCTION_IDS_DOOR_OPENER:
            return {
                    "inputs": [
                        PID_TIMED_START_STOP,
                        ],
                    "outputs": [
                        PID_INFO_ON_OFF,
                        ]
                    }

    async def open(self):
        """Trigger the door opener pulse."""
        if PID_TIMED_START_STOP in self._datapoints:
            dp = self._datapoints[PID_TIMED_START_STOP]
            await self.client.set_datapoint(self.serialnumber, self.channel_id, dp, '1')
        else:
            LOG.warning("Door opener %s (%s) missing timed start/stop datapoint", self.name, self.lookup_key)

    async def lock(self):
        if PID_TIMED_START_STOP in self._datapoints:
            dp = self._datapoints[PID_TIMED_START_STOP]
            await self.client.set_datapoint(self.serialnumber, self.channel_id, dp, '0')
        else:
            LOG.warning("Door opener %s (%s) missing timed start/stop datapoint", self.name, self.lookup_key)

    async def unlock(self):
        await self.open()

    def update_datapoint(self, dp, value):
        """Receive updated datapoint."""
        if self._datapoints.get(PID_INFO_ON_OFF) == dp:
            self.state = value
            LOG.info("lock device %s (%s) dp %s state %s", self.name, self.lookup_key, dp, value)

        else:
            LOG.info("lock device %s (%s) unknown dp %s value %s", self.name, self.lookup_key, dp, value)
            
    def update_parameter(self, param, value):
        LOG.debug("Not yet implemented")