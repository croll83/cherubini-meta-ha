# Cherubini META – Home Assistant

Integrazione **locale** (no cloud) per il gateway **Cherubini METAHome**: controlla le
tapparelle radio 433 MHz (`CC_CH_433_TAPPARELLA`) parlando direttamente con l'API HTTP
locale del gateway.

## Funzionalità
- **Config flow**: basta IP del gateway + username + password.
- **Auto-discovery** di tutte le tapparelle dal gateway.
- Entità `cover` per ogni tapparella: **apri / chiudi / stop** + **posizione/stato**
  (0 = chiusa, 100 = aperta, sconosciuta se mai operata).
- Entità `button` "Livello predefinito" per ogni tapparella (comando *preferred position*).
- 100% locale, polling dello stato dal gateway.

## Installazione (HACS)
1. HACS → Integrazioni → menu ⋮ → *Repository personalizzati* → aggiungi questo repo (categoria *Integration*).
2. Installa "Cherubini META", riavvia Home Assistant.
3. Impostazioni → Dispositivi e servizi → *Aggiungi integrazione* → "Cherubini META".
4. Inserisci IP gateway, username e password (consigliata un'utenza dedicata).

## Note
- Il gateway tiene **una sola sessione per utente**: usa un account dedicato per HA per non sloggare l'app sul telefono.
- Le tapparelle radio non hanno feedback di posizione assoluto: lo stato riflette il livello stimato dal gateway.

## Logo nell'interfaccia HA
Per mostrare il logo Cherubini in Impostazioni → Dispositivi e servizi serve un PR al repo
[home-assistant/brands](https://github.com/home-assistant/brands) con `icon.png`/`logo.png` sotto `custom_integrations/cherubini_meta/`.
