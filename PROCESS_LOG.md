# PROCESS_LOG.md – Zurich Tram Data

> Projektverlauf und AI-Kontext-Einstieg.
> Dieses File ist der Einstiegspunkt für neue Claude-Sessions.

---

## Projekt-Übersicht

| Feld | Inhalt |
| :--- | :--- |
| Projektname | Zurich Tram Data |
| Erstellt | 2026-07-02 |
| Status | 🟢 Setup — Content migriert, Notebooks noch nicht durchlaufen |
| Nächster Schritt | Notebooks 00–08 der Reihe nach ausführen, Master-Datensatz neu erzeugen, `/project-review` als ersten Audit-Loop |

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
