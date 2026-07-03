# PROCESS_LOG.md – Zurich Tram Data

> Projektverlauf und AI-Kontext-Einstieg.
> Dieses File ist der Einstiegspunkt für neue Claude-Sessions.

---

## Projekt-Übersicht

| Feld | Inhalt |
| :--- | :--- |
| Projektname | Zurich Tram Data |
| Erstellt | 2026-05-07 |
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

### 2026-07-03 — `/project-review` Audit-Loop + Konsistenz-Fixes

`/project-review` gelaufen (zweiter `wgnd-ai-dev-toolchain`-Testpunkt, ROADMAP Phase 2). Ergebnis:
kein blockierender Fehler, Fundament solide. Befunde waren Konsistenz-Drift + stage-gerechte
Portfolio-Lücken (index.html noch Platzhalter — Phase 3, erwartbar).

Umgesetzte Fixes (ein Commit):
- **Typ DAN → DE** vereinheitlicht (`CLAUDE.md`, pyproject-Description, `docs/PROJECTS.md`). README war
  bereits „Data Engineering". Der `[dan]`-pip-Extra bleibt bewusst — Scaffolding-Mechanismus-Slot
  (bündelt plotly/folium), kein Typ-Label.
- **Erstell-Datum** in `PROCESS_LOG` auf `2026-05-07` gezogen (Deckung mit README; Session-Daten unberührt).
- **`docs/PROJECTS.md`** Phasenstand `1 — Setup` → `1 — Notebooks ✅`.
- **Git-Hygiene:** `notebooks/appendix/` untracked (`git rm --cached` + `.gitignore`) — ~11 MB Map-Blobs
  (folium/plotly) raus aus dem öffentlichen Repo, lokal erhalten.

Bewusst **nicht** angefasst: Backlog #1/#2 (inhaltliche Entscheidung, kein Konsistenz-Fix).

**Toolchain-Befund:** Die `/project-review`-Skill prüft in Schritt 2 hart auf `reports/index.html`,
das Scaffolding erzeugt aber `public/` (Schritt 3.5+ referenziert korrekt `public/`) — interner
Pfad-Widerspruch in der Skill. Kay passt die Skill in separater Session an.

**Nächster Schritt:** Phase 2 abschließen — Backlog #1/#2 (trip_id-Brücke / `UMLAUF_ID`) als Entscheidung
durchgehen, bevor ein Reprocessing ansteht.

---

### 2026-07-03 (Fortsetzung) — `index.html` mit Inhalt + Asset-Struktur deployment-fest

- **README:** `## TL;DR` vor `## Projekt` ergänzt (results-first, nur die wichtigsten Fakten). Zahlen
  stammen aus vorhandenen README-Sections, nicht frisch aus Notebooks kopiert.
- **`public/index.html`:** vom Scaffold-Platzhalter zu echtem Inhalt — Lead-Beschreibung plus
  Motivation / Beschreibung / Datenquellen / Prozess / Ergebnis, 1:1 aus README `## Projekt`
  übernommen (jede `###` → `<h2>`, Markdown → HTML).
- **Asset-Struktur deployment-fest gemacht:** `assets/` aufgelöst → beide SVGs nach `public/img/`
  (getrackt). Referenzen: `index.html` via `img/…`, README via `public/img/…`. Grund: `public/` wird
  in Phase 3 GitHub-Pages-Root — der vorherige `../assets/`-Pfad hätte über den Site-Root
  hinausgezeigt (404 beim Deployment). Damit ist der Deployment-Pfad-Punkt erledigt, nicht nur vertagt.
- **geopandas-Explorations-PDFs** (3×) wie die Appendix aus Git genommen (`git rm --cached` +
  `.gitignore`), lokal in `public/img/` erhalten.

Offen (Phase 3, bewusst vertagt): Datenquellen-Tabelle in `index.html` unstyled. BACKLOG #1/#2
unverändert offen — relevant erst bei einem Reprocessing.

**Nächster Schritt:** unverändert — Phase 2 (Backlog-Entscheidung) vor vollständigem Phase-3-Ausbau.

---

### 2026-07-03 (Fortsetzung) — `/project-review` #2 + Notebooks-Tabelle, drei Toolchain-Findings behoben

Zweiter `/project-review`-Durchlauf (Fundament solide, keine Blocker). Ergebnis: die Kern-Lücken
waren **Toolchain-Findings**, nicht Projekt-Findings — genau der Zweck von zh-tram-data als
`wgnd-ai-dev-toolchain`-Testlauf. In `wgnd-scaffolding` + `wgnd-skills` gefixt (dort eigene Commits):

- **A — Report-Link fehlte im Scaffold:** `readme_template.py` erzeugte nie eine Section, die auf
  `public/index.html` verweist. Standard-`## Report`-Section ergänzt → alle künftigen Projekte ab Tag 1.
- **B — Notebooks-Liste dreifach gepflegt / gedriftet:** README-Struktur-Tree war im Template
  hartkodiert und hing dem Notebook-Generator hinterher (zeigte alte DS-Namen). Fix: `get_notebook_index()`
  aus einer neuen `_specs()`-**Single-Source** in `notebooks_da/ds.py`; README rendert Tree + verlinkte
  Notebooks-Tabelle daraus. Drift strukturell ausgeschlossen.
- **C — `/project-review` PNG-fixiert:** harter „min. 3 PNG"-Check → format-agnostisch (PNG/SVG egal,
  DE-Projekte liefern SVG-Diagramme) + weicher Verlinkungs-Check.

**Für dieses Projekt** (Nachtrag von Hand, da Notebooks migriert statt scaffold-generiert):
verlinkte Notebooks-Tabelle (`00`–`08`) + `## Report`-Section in die README, `index.html`-Titel
„Executive Summary" → „Data Engineering Case". Alle 9 Notebook-Links gegen echte Files geprüft.

**Toolchain-Arbeitsteilung bestätigt:** Scaffolding = korrekt bei Geburt (keine Template-Drift),
`/project-review` = laufende Wachsamkeit über die Projekt-Lebenszeit (fängt Migrations-Drift wie hier).

Zwei neue Findings ins `docs/BACKLOG.md` (nicht gefixt): CLI akzeptiert kein `DE` (scaffolding #11),
`portfolio-readme-template.md` hat dieselbe PNG-Fixierung (Workspace/Infra #20).

**Nächster Schritt:** unverändert — Phase 2 Backlog-Entscheidung (#1/#2, trip_id-Brücke / `UMLAUF_ID`)
vor Phase-3-Ausbau. README-Restpunkte offen: Author-Section, Sprach-Entscheidung DE/EN.

---
