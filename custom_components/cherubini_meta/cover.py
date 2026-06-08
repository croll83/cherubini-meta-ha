"""Piattaforma cover per le tapparelle Cherubini META."""
from __future__ import annotations

from homeassistant.components.cover import (
    CoverEntity, CoverEntityFeature, CoverDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import CherubiniEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        CherubiniCover(coordinator, ifd, data)
        for ifd, data in coordinator.data.items()
    )


class CherubiniCover(CherubiniEntity, CoverEntity):
    """Una tapparella 433."""

    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
    )

    def __init__(self, coordinator, ifd, data) -> None:
        super().__init__(coordinator, ifd, data)
        self._attr_unique_id = f"cherubini_{ifd}"
        self._attr_name = None

    @property
    def current_cover_position(self):
        """0 = chiusa, 100 = aperta, None = sconosciuta."""
        return self._data.get("position")

    @property
    def is_closed(self):
        pos = self._data.get("position")
        return None if pos is None else pos == 0

    async def async_open_cover(self, **kwargs) -> None:
        await self.coordinator.api.control(self._ifd, "up")

    async def async_close_cover(self, **kwargs) -> None:
        await self.coordinator.api.control(self._ifd, "down")

    async def async_stop_cover(self, **kwargs) -> None:
        await self.coordinator.api.control(self._ifd, "stop")
