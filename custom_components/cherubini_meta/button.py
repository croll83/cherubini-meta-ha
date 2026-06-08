"""Pulsante 'livello predefinito' per ogni tapparella."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import CherubiniEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        CherubiniPreferredButton(coordinator, ifd, data)
        for ifd, data in coordinator.data.items()
    )


class CherubiniPreferredButton(CherubiniEntity, ButtonEntity):
    """Porta la tapparella alla posizione preferita (comando MY)."""

    _attr_icon = "mdi:star-outline"

    def __init__(self, coordinator, ifd, data) -> None:
        super().__init__(coordinator, ifd, data)
        self._attr_unique_id = f"cherubini_{ifd}_preferred"
        self._attr_name = "Livello predefinito"

    async def async_press(self) -> None:
        await self.coordinator.api.control(self._ifd, "my")
