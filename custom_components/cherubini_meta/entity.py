"""Entity base condivisa."""
from __future__ import annotations
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import CherubiniCoordinator


class CherubiniEntity(CoordinatorEntity[CherubiniCoordinator]):
    """Base per cover e button di una tapparella."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: CherubiniCoordinator, ifd: str, data: dict) -> None:
        super().__init__(coordinator)
        self._ifd = ifd
        self._base_name = f"Tapparella {data['name']}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, ifd)},
            name=self._base_name,
            manufacturer="Cherubini",
            model="META 433 Tapparella",
        )

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get(self._ifd, {})

    @property
    def available(self) -> bool:
        return super().available and self._ifd in self.coordinator.data
