# BACKLOG.md – Zurich Tram Data

Projektspezifische offene Tasks und Todos.
Nie mitten in einer Session den Kontext wechseln — hier notieren, gesammelt abarbeiten.

Prio: `1` = hoch · `2` = mittel · `3` = niedrig

---

| # | Beschreibung | Prio | Entdeckt in |
| :--- | :--- | :--- | :--- |
| 1 | **trip_id zwischen IST-Daten und GTFS ist nicht direkt matchbar** — IST-`FAHRT_BEZEICHNER` hat Format `85:3849:…`, GTFS-`trip_id` hat Format `1.T0.1-10-P-j23-…` → 0% String-Overlap, kein direkter Join. War Grund für die Entfernung des Fahrtrichtungs-Filters im zh-tram-flow-Dashboard (#67b). Prüfen: gibt es eine Umlauf-/Fahrplan-basierte Brücke (z.B. über `LINIEN_TEXT` + `ANKUNFTSZEIT` + `BPUIC`-Sequenz) um beide Systeme zu verknüpfen? Wäre Voraussetzung für richtungsspezifische Analysen und für `prev_trip_delay`/Kaskadeneffekt (F-NET-07, bisher unanalysiert). | 1 | zh-tram-flow `PROCESS_LOG.md:1727`, 2026-06-25 |
| 2 | **Zu viele Rohspalten beim IST-Daten-Processing verworfen** — `KEEP_COLS` in `02_ingestion-ist.ipynb` behält nur 10 von ursprünglich ~20+ Spalten. Dauerhaft verloren (nicht mal transient genutzt): `UMLAUF_ID` (Fahrzeug-/Umlauf-Kennung — könnte die eigentliche Brücke für Kaskadeneffekt-Analyse sein, direkter als trip_id-Kontinuität), `AN_PROGNOSE_STATUS`/`AB_PROGNOSE_STATUS` (Datenqualitäts-Flag, nur für Filter genutzt dann verworfen), `VERKEHRSMITTEL_TEXT`, `HALTESTELLEN_NAME` (Rohname vor GTFS-Join), `BETREIBER_ABK`/`BETREIBER_NAME`. Nachträgliches Hinzufügen bedeutet volles Reprocessing ab den Roh-ZIPs (liegen nur auf externer Platte, nicht im Repo) — vor `02_ingestion-ist` prüfen, ob `UMLAUF_ID` mit aufgenommen werden soll, bevor die Parquets erneut geschrieben werden. | 2 | `src/zh_tram_data/process_ist_daten.py` + `02_ingestion-ist.ipynb`, Migrations-Session 2026-07-02 |
