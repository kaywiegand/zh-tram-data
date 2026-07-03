# PROCESS_LOG.md – Zurich Tram Data

> Projektverlauf und AI-Kontext-Einstieg.
> Dieses File ist der Einstiegspunkt für neue Claude-Sessions.

---

## Projekt-Übersicht

| Feld | Inhalt |
| :--- | :--- |
| Projektname | Zurich Tram Data |
| Erstellt | 2026-07-02 |
| Status | 🟢 Phase 1 abgeschlossen — alle 9 Notebooks laufen fehlerfrei, `vbz_master.parquet` reproduziert (94.358.531 Zeilen × 26 Spalten, deckungsgleich mit Original) |
| Nächster Schritt | Backlog-Punkte (trip_id-Mismatch, fehlende Spalten) sichten, dann `/project-review` als Audit-Loop |

---

## Verlauf

### 2026-07-02 – Projekt aufgesetzt (erster echter Test von `wgnd-ai-dev-toolchain`)

- `/project-init` → `wgnd-scaffolding` (Typ DAN) — lief ohne Reibung durch, Git-Init +
  Erstcommit + `docs/PROJECTS.md`-Eintrag automatisch/skill-geführt.
- Zweck: `sf_data-research` ist die Data-Engineering-Vorstufe für `zh-tram-flow`, enthält aber
  neben den Zürich-Daten (VBZ) auch einen Berlin-Vergleichsabstecher (VBB). Dieses Projekt
  isoliert nur den Zürich-Teil als eigenständiges, portfolio-fähiges DE-Case — Gegenstück zu
  `zh-tram-flow` (Analyse/ML), Fokus auf ETL/Datenqualität/Architektur statt Modellierung.

**Notebook-Migration** (17 Quell-Notebooks aus `sf_data-research/notebooks/vbz/` → 9 nummerierte
+ Appendix, siehe Chat-Verlauf für die vollständige Zuordnungstabelle):
- `00_introduction` (Strategie + Datenlandschaft, gemergt aus 2 Quellen)
- `01_tooling-evaluation` (Pandas vs. Polars — bewusste Werkzeugwahl vor dem Start)
- `02_ingestion-ist`, `03_ingestion-gtfs` (je 2 Quellen gemergt), `04_ingestion-meteo`,
  `05_ingestion-events` — vier Ingestion-Schritte
- `06_geo-reference` (Benchmark-Ergebnis, nicht alle Tool-Varianten einzeln)
- `07_master-preparation`, `08_master-validation` — Join + Validierung als Abschluss
- `notebooks/appendix/`: 5 Geo-Map-Bibliotheksvarianten (folium/geopandas/kepler/plotly + generisch)
  — Explorationsmaterial, bewusst nicht im nummerierten Hauptpfad

**Weitere Migration:**
- `src/zh_tram_data/doc_loader.py` + `process_ist_daten.py` aus `sf_data-research/src/`
  übernommen, Pfade angepasst (kein `vbz/`-Zwischenordner mehr nötig — dieses Projekt ist
  Zürich-only, kein Berlin-Geschwister wie im Ursprungsprojekt)
- `data/raw/` (2.3 GB) + `data/interim/` (1.9 GB) lokal kopiert, ebenfalls ohne `vbz/`-Ebene —
  gitignored, nicht Teil des Commits

**Notebooks noch nicht ausgeführt** — Migration ist strukturell, Inhalte (Zellen 1:1 übernommen)
müssen noch mit aktueller `.venv` durchlaufen und validiert werden.

**Toolchain-Test-Ergebnis:** `/project-init` lief reibungslos. Nächster Baustein ist
`/project-review` als Audit-Loop, sobald die Notebooks laufen — zweiter echter Testpunkt für
`wgnd-ai-dev-toolchain`.

---

### 2026-07-02 (Fortsetzung) — Notebooks 00–08 lauffähig gemacht, 3 echte Bugs gefunden

venv aufgesetzt (`uv venv` + `uv pip install -e ".[dan]"`), dabei fehlende Dependencies im
DAN-Template nachgetragen: `polars`, `geopandas`, `shapely`, `psutil`, `requests` waren nicht in
`pyproject.toml` — nur Standard-DAN-Stack (pandas/numpy/sklearn/...), aber diese Notebooks
brauchen mehr. Alle 9 Notebooks (`00`–`08`) danach der Reihe nach mit `jupyter nbconvert
--execute --inplace` durchlaufen lassen. Drei echte Bugs dabei gefunden und gefixt:

**1. Kaputte Pfade durch die Migration** (vor der ersten Ausführung schon gefixt, siehe oben):
relative Tiefe (`../../` vs. `../`), `vbz/`-Zwischenordner-Reste (auch in `07_master-preparation`
noch 2 Stellen übersehen — `EVENTS_DIR`/`OUT_DIR` zeigten auf ein nicht mehr existierendes
`data/interim/vbz/`), Root-Finder-Anker (`reports` existiert im neuen Scaffold nicht, auf `data`
umgestellt), fehlende Assets (`assets/vbz_strategy.svg`, `assets/vbz_preparation.svg` nachkopiert),
ein vorbestehender Tippfehler im Original (`data/raw/vbz/stadtkreise/data` → richtig `geo/data`,
betraf `06_geo-reference` + 4 Appendix-Notebooks).

**2. `02_ingestion-ist` nicht idempotent:** Die KEEP_COLS-Reduktionszelle liest Rohspalten
(`AN_PROGNOSE_STATUS` etc.), berechnet Delays + `stop_sequence`, und überschreibt die
Interim-Parquets dabei destruktiv mit nur noch 10 Spalten. Die kopierten Interim-Daten waren
aber bereits das fertig-reduzierte Ergebnis (bestätigt Kays Backlog-Punkt #2 zu den verworfenen
Spalten) — zweiter Lauf gegen bereits reduzierte Daten warf `KeyError: 'AN_PROGNOSE_STATUS'`.
Fix: Zelle prüft jetzt, ob die Rohspalte noch existiert, und überspringt die Reduktion sonst
(„resume-fähig", passend zur bestehenden Konvention in `process_ist_daten.py`).

Dieselbe Zelle hatte eine zweite, unabhängige Blockade: eine live Download-Demo
(„Demo: Einzelner Monat, ausführbar") lud unbegrenzt (kein Timeout auf `requests.get`) vom
OTD-Swiss-Archiv — ließ den automatisierten Lauf nach 900s timeout. Hinter `RUN_DEMO = False`
gesetzt (Standard aus), analog zur bereits auskommentierten `download_monthly_zips()`-Zelle
direkt davor im selben Notebook — für manuelles interaktives Ausführen weiter nutzbar.

**3. `07_master-preparation`: Datetime-Precision-Mismatch beim Meteo-Join.** `meteo_pl` wird via
`pl.from_pandas(pd.read_parquet(...))` gebaut — der Pandas-Roundtrip liefert `datetime[ns]`,
während die IST-Daten nativ `datetime[us]` sind. Polars' `SchemaError` beim Join auf den
stundengerundeten Schlüssel `_h`. Fix: `date_time` explizit auf `pl.Datetime('us')` gecastet
beim Aufbau von `meteo_pl`.

**Ergebnis:** `data/interim/vbz_master.parquet` — 94.358.531 Zeilen × 26 Spalten. Identisch mit
dem Original in `sf_data-research` (siehe dortiges `PROCESS_LOG.md`, Nachtrag 2026-05-15).

**Toolchain-Test-Fazit:** `/project-init` lief reibungslos (siehe oben). Der eigentliche Content
— Notebooks + Daten — kam aber nicht über den Skill, sondern manuell migriert; das war erwartet
(`/project-init`/`wgnd-scaffolding` bauen ein leeres Skelett, keine Migration aus Altprojekten).
Alle drei gefundenen Bugs lagen im migrierten Notebook-Code selbst, nicht im Toolchain-Mechanismus.

**Nächster Schritt:** Backlog-Punkte sichten (trip_id-Mismatch IST↔GTFS, fehlende Spalten wie
`UMLAUF_ID`), dann `/project-review` als Audit-Loop — zweiter echter Testpunkt für
`wgnd-ai-dev-toolchain`.

---
