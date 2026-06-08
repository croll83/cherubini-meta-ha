"""Coordinator: polling periodico del dashboard del gateway."""
from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CherubiniMetaApi, CherubiniApiError
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class CherubiniCoordinator(DataUpdateCoordinator):
    """Tiene aggiornato lo stato delle tapparelle."""

    def __init__(self, hass: HomeAssistant, api: CherubiniMetaApi) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            covers = await self.api.get_covers()
        except CherubiniApiError as err:
            raise UpdateFailed(str(err)) from err
        return {c["ifd"]: c for c in covers if c.get("ifd")}
