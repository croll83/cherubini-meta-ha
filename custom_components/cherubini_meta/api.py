"""Client per l'API locale del gateway Cherubini METAHome."""
from __future__ import annotations
import asyncio
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

# mappa azione -> (nome comando, frame 433 grezzo)
CMD = {
    "up":   ("fullOn",            "05,07,01"),
    "down": ("fullOff",           "01,07,01"),
    "stop": ("stop",              "0A,0A,01"),
    "my":   ("preferredPosition", "0A,1E,01"),
}
_HEADERS = {"appid": "metaCherubini", "content-type": "application/json"}


class CherubiniApiError(Exception):
    """Errore generico API."""


class CherubiniAuthError(CherubiniApiError):
    """Credenziali errate / sessione non valida."""


class CherubiniMetaApi:
    """Parla con il gateway METAHome via la sua API HTTP locale."""

    def __init__(self, session: aiohttp.ClientSession, host: str,
                 username: str, password: str) -> None:
        self._session = session
        self._host = host
        self._user = username
        self._pass = password
        self._token: str | None = None
        self._lock = asyncio.Lock()

    @property
    def _base(self) -> str:
        return f"http://{self._host}"

    async def _post(self, path: str, body: dict, auth: bool = True):
        headers = dict(_HEADERS)
        if auth:
            headers["authorization"] = self._token or ""
        try:
            async with self._session.post(
                self._base + path, json=body, headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                return resp.status, await resp.text()
        except aiohttp.ClientError as err:
            raise CherubiniApiError(f"connessione fallita: {err}") from err
        except asyncio.TimeoutError as err:
            raise CherubiniApiError("timeout") from err

    async def login(self) -> dict:
        import json
        status, text = await self._post(
            "/api/zCmd/login",
            {"uriAPI": "/register/login",
             "uriData": {"usrname": self._user, "passwd": self._pass, "email": ""}},
            auth=False,
        )
        if status != 200:
            raise CherubiniAuthError(f"login HTTP {status}")
        try:
            data = json.loads(text)
        except ValueError as err:
            raise CherubiniApiError("risposta login non valida") from err
        token = data.get("widToken")
        if not token:
            raise CherubiniAuthError("credenziali errate")
        self._token = token
        return data

    async def _auth_post(self, path: str, body: dict):
        if not self._token:
            await self.login()
        status, text = await self._post(path, body)
        if status in (401, 403):
            await self.login()
            status, text = await self._post(path, body)
        return status, text

    async def get_dashboard(self) -> list:
        import json
        async with self._lock:
            status, text = await self._auth_post(
                "/api/lCmd/getFullDashboard",
                {"uriAPI": "/dashboard/getFullDashboard", "uriData": {}})
        if status != 200:
            raise CherubiniApiError(f"dashboard HTTP {status}")
        try:
            return json.loads(text)
        except ValueError as err:
            raise CherubiniApiError("dashboard non valida") from err

    async def control(self, ifd: str, action: str) -> None:
        uri_api, frame = CMD[action]
        body = {"uriAPI": uri_api,
                "uriData": {"ifd": ifd,
                            "cmdBytes": [{"data": frame + "\r", "delay": 0}]}}
        async with self._lock:
            status, _ = await self._auth_post("/api/ch433Cmd/control", body)
        if status != 200:
            raise CherubiniApiError(f"control HTTP {status}")

    async def get_covers(self) -> list[dict]:
        """Scopre le tapparelle dal dashboard."""
        from .const import IF_TAPPARELLA
        covers = []
        for nd in await self.get_dashboard():
            itf = nd.get("interface", {}) or {}
            if itf.get("name") != IF_TAPPARELLA:
                continue
            ad = nd.get("additional", {}) or {}
            st = (itf.get("statusData") or {}).get("state")
            pos = int(st) if isinstance(st, (int, float)) and 0 <= st <= 100 else None
            covers.append({
                "ifd": itf.get("if_desc"),
                "n_id": nd.get("n_id"),
                "name": ad.get("epName") or ad.get("roomName") or str(nd.get("n_id")),
                "room": ad.get("roomName"),
                "position": pos,
            })
        return covers
