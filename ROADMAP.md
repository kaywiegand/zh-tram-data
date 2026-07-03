# ROADMAP.md – Zurich Tram Data

> Data-Engineering-Pipeline für VBZ-Tramdaten — Ausgangslage → Phasen → Ziel.
> Zürich-Teil aus `sf_data-research` isoliert (das Projekt hatte zusätzlich einen
> Berlin/VBB-Vergleichsabstecher, der hier bewusst nicht mitkommt).

---

## Ausgangslage

`sf_data-research` hatte die Data-Engineering-Phase bereits abgeschlossen (Download, Filter,
Join, Validierung — siehe dortiges `ROADMAP.md`, Phase 0 ✅). Dieses Projekt migriert den
Zürich-Teil in eine eigenständige, portfolio-fähige Struktur und macht ihn erneut lauffähig —
zugleich der erste echte Testlauf von `wgnd-ai-dev-toolchain`.

---

## Phase 0 — Setup & Migration ✅ ABGESCHLOSSEN

- [x] Projektstruktur mit `wgnd-scaffolding` generiert (Typ DAN)
- [x] Notebook-Migration aus `sf_data-research/notebooks/vbz/`: 17 Quell-Notebooks →
      9 nummerierte (`00`–`08`) + `notebooks/appendix/` für Explorationsmaterial
- [x] `src/` migriert (`doc_loader.py`, `process_ist_daten.py`), Pfade angepasst
- [x] Daten kopiert (`data/raw/` 2.3 GB, `data/interim/` 1.9 GB), `vbz/`-Zwischenordner entfernt
- [x] Gebrochene Pfad-Referenzen gefixt (relative Tiefe, `vbz/`-Segmente, Root-Finder-Anker,
      fehlende Assets nachgezogen — `assets/vbz_strategy.svg`, `assets/vbz_preparation.svg`)
- [x] venv aufgesetzt, fehlende Dependencies ergänzt (`polars`, `geopandas`, `shapely`,
      `psutil`, `requests` fehlten im DAN-Template — nachgetragen in `pyproject.toml`)

---

## Phase 1 — Notebooks lauffähig machen (00–08) ✅ ABGESCHLOSSEN

- [x] `00_introduction` — Strategie + Datenlandschaft
- [x] `01_tooling-evaluation` — Pandas vs. Polars
- [x] `02_ingestion-ist` — IST-Verspätungsdaten (Bug gefunden + gefixt: nicht-idempotente
      Zelle, blockierender Live-Download — siehe `PROCESS_LOG.md`)
- [x] `03_ingestion-gtfs` — GTFS-Referenzdaten + Stadtkreis-Join
- [x] `04_ingestion-meteo` — Wetterdaten (3 Quellen)
- [x] `05_ingestion-events` — Event-Kalender
- [x] `06_geo-reference` — Geo-Bibliotheks-Benchmark + Stadtkreis-Zuordnung
- [x] `07_master-preparation` — Join IST+GTFS+Meteo+Events → Master-Datensatz (Bug gefunden +
      gefixt: Datetime-Precision-Mismatch beim Meteo-Join, stale `vbz/`-Pfadreste)
- [x] `08_master-validation` — Validierung

**Ergebnis:** `vbz_master.parquet` — 94.358.531 Zeilen × 26 Spalten, deckungsgleich mit dem
Original in `sf_data-research`.

---

## Phase 2 — Qualitätssicherung

- [ ] Offene Backlog-Punkte aus der Migration prüfen (trip_id-Mismatch, fehlende Spalten —
      siehe `BACKLOG.md`)
- [x] `/project-review` als Audit-Loop — zweiter echter Test von `wgnd-ai-dev-toolchain`
      (2026-07-03: kein blockierender Fehler, Konsistenz-Fixes umgesetzt — siehe `PROCESS_LOG.md`)
- [ ] README, CLAUDE.md, Stack-Angaben finalisieren

---

## Phase 3 — Portfolio-Aufbereitung

- [x] `/project-case` — Engineering-Case gebaut (engineering-first, 6 Kapitel: Reduktion + Anreicherung
      als zwei Bögen; Hub + overview/storyview/techview aus `slides.yaml` generiert). 2026-07-03.
- [ ] Deployment (`public/` → GitHub Pages)
- [ ] `00_introduction`: stale IST-Reduktion „21 → 8" → „21 → 10" korrigieren (NotebookEdit)

---

## Ziel

Ein eigenständiges, reproduzierbares DE-Portfolio-Case: Recherche → Sammlung → Bearbeitung →
Zusammenführung → Validierung → Bereitstellung, sauber dokumentiert und nachvollziehbar — als
Gegenstück zu `zh-tram-flow` (Analyse/ML) und als zweiter Beleg für `wgnd-ai-dev-toolchain`.
