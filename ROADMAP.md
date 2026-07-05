# ROADMAP.md – Zurich Tram Data

> Data-Engineering-Pipeline für VBZ-Tramdaten — Ausgangslage → Phasen → Ziel.
> Zürich-Teil aus einem vorangegangenen, breiter angelegten Data-Research-Projekt isoliert
> (das zusätzlich einen Berlin/VBB-Vergleichsabstecher hatte, der hier bewusst nicht mitkommt).

---

## Ausgangslage

Die Data-Engineering-Phase (Download, Filter, Join, Validierung) war in einem vorangegangenen,
breiter angelegten Research-Projekt bereits abgeschlossen. Dieses Projekt isoliert den
Zürich-Teil in eine eigenständige, portfolio-fähige Struktur und macht ihn erneut lauffähig —
zugleich der erste echte Testlauf von `wgnd-ai-dev-toolchain`.

---

## Phase 0 — Setup & Migration ✅ ABGESCHLOSSEN

- [x] Projektstruktur mit `wgnd-scaffolding` generiert (Typ DAN)
- [x] Notebook-Migration aus dem Vorgänger-Repo (`notebooks/vbz/`): 17 Quell-Notebooks →
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
ursprünglich erzeugten Referenz-Datensatz (validiert in `08_master-validation`).

---

## Phase 2 — Qualitätssicherung

- [x] Offene Migrations-Findings entschieden: trip_id-Mismatch + verworfene Rohspalten sind
      **keine offenen Tasks**, sondern Scope-Grenzen dieser Auflage (Reprocessing ab Roh-ZIPs
      nötig) → als **OP-1/OP-2** in die „Future / Opportunities"-Sektion umgewidmet (siehe unten
      + `BACKLOG.md`)
- [x] `/project-review` als Audit-Loop — zweiter echter Test von `wgnd-ai-dev-toolchain`
      (2026-07-03: kein blockierender Fehler, Konsistenz-Fixes umgesetzt — siehe `PROCESS_LOG.md`)
- [x] README auf Englisch + an `zh-tram-flow`-Struktur angeglichen (TL;DR, Where-to-start, TOC,
      Author) — 2026-07-04
- [ ] CLAUDE.md-Stack-Angabe (Polars · Plotly · Jupyter) um GeoPandas/Shapely ergänzen (minor)

---

## Phase 3 — Portfolio-Aufbereitung

- [x] `/project-case` — Engineering-Case gebaut (engineering-first, 6 Kapitel: Reduktion + Anreicherung
      als zwei Bögen; Hub + overview/storyview/techview aus `slides.yaml` generiert). 2026-07-03.
- [ ] Deployment (`public/` → GitHub Pages)
- [x] `00_introduction`: stale IST-Reduktion „21 → 8" → „21 → 10" korrigiert; zusätzlich
      `FAHRT_BEZEICHNER` aus der „Entfernte Spalten"-Tabelle entfernt (wird als `trip_id`
      behalten — Widerspruch zu `KEEP_COLS` aufgelöst). 2026-07-04.

---

## Future / Opportunities (OP) — bewusst nicht in v1

Erweiterungen, die ein **volles Reprocessing ab den Roh-ZIPs** voraussetzen (liegen nur auf
externer Platte, nicht im Repo). Bewusste Scope-Grenzen dieser Auflage — kein offener Task,
kein Blocker. Erst bei einer Neuauflage / v2 relevant. Gegenstück zu `zh-tram-flow`s Phase 6.

| OP # | Thema | Prio | Nächster Schritt bei v2 |
| :--- | :--- | :--: | :--- |
| **OP-1** | trip_id-Brücke IST↔GTFS (Voraussetzung für Richtungs- + Kaskaden-Analyse) | 1 | Fahrplanbasierte Brücke über `LINIEN_TEXT`+`ANKUNFTSZEIT`+`BPUIC` prüfen |
| **OP-2** | `UMLAUF_ID` + weitere Rohspalten beim IST-Processing behalten | 2 | Vor Neu-Schreiben der IST-Parquets `KEEP_COLS` erweitern |

→ **Detailliert:** `BACKLOG.md` — Sektion „🔬 Research Opportunities & Future Reprocessing (OP)"

---

## Ziel

Ein eigenständiges, reproduzierbares DE-Portfolio-Case: Recherche → Sammlung → Bearbeitung →
Zusammenführung → Validierung → Bereitstellung, sauber dokumentiert und nachvollziehbar — als
Gegenstück zu `zh-tram-flow` (Analyse/ML) und als zweiter Beleg für `wgnd-ai-dev-toolchain`.
