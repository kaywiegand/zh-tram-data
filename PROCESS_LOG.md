# PROCESS_LOG.md – Zurich Tram Data

> Projektverlauf und AI-Kontext-Einstieg.
> Dieses File ist der Einstiegspunkt für neue Claude-Sessions.

---

## Projekt-Übersicht

| Feld | Inhalt |
| :--- | :--- |
| Projektname | Zurich Tram Data |
| Erstellt | 2026-05-07 |
| Status | 🟢 Phase 2 abgeschlossen, Phase 3 in Arbeit — Styleguide v2 ausgerollt, alle 3 Views komplett reviewed |
| Nächster Schritt | `wgnd-skills`-Branch `feature/styleguide-v2` mergen, dann Deployment (`public/` → GitHub Pages) |

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

### 2026-07-03 (Fortsetzung) — `/project-case`: DE-Portfolio-Case gebaut + Hub-Prosa-Toolchain-Fix

`/project-case check → story → slides → report` auf zh-tram-data. Erster **engineering-first**
Portfolio-Case im Workspace — das Case-Template ist auf Analyse/ML geschnitten (Findings, Model-MAE,
Recommendations), musste für DE umgedeutet werden.

**Phase-2-Entscheidung (Kay):** Backlog #1/#2 (trip_id-Brücke / `UMLAUF_ID`) bleiben offen — sind
Reprocessing-Kandidaten für eine **Projektneuauflage**, nicht für jetzt. Der Master wird as-is
verwendet, die Grenzen werden als Known Limitations Teil der Story (Transparenz als DE-Signal).

**DE-Adaption des Case (P2-Blueprint, an echtem Case definiert statt abstrakt):**
- Kernthese: „Reduzieren was da ist, anreichern was fehlt" — zwei Bögen (Reduktion + Anreicherung).
- Mapping: Key Findings → **Engineering Decisions** · Model Results → **Data Quality & Pipeline** ·
  Recommendations → **Known Limitations**.
- `slides.yaml`: 6 Kapitel, StoryView (voll, 20 Slides) → TechView (19, mit 3 tech-exklusiven
  Evidenz-Slides: Polars-Detail, Data Dictionary, Validierung) → Overview (10, verdichtet). Beide
  Prozess-SVGs eingebettet.

**Zahlen gegen echte Artefakte verifiziert** (nichts erfunden): Master-Parquet-Schema gelesen →
**26 Spalten = 10 IST · 3 GTFS · 2 Geo · 7 Meteo · 4 Events**; KEEP_COLS im Code = **10** (nicht 8).
→ Offenes Finding: `00_introduction` sagt IST-Reduktion „21 → 8", korrekt ist „21 → 10" — Notebook-Text
nachziehen (NotebookEdit, mit Kays OK). Vermerkt im `portfolio.md` Status-Block.

**Toolchain-Fix (in wgnd-skills, eigener Commit):** `index-template.html` enthielt hartcodierte
zh-tram-flow-Prosa (Tagline, „Das Projekt"-Sektion, Quick-Links, Footer) — jedes andere Projekt bekam
dessen Story in seinen Hub. Parametrisiert: Tagline/Subtitle/About/Quick-Links/Footer kommen jetzt aus
dem `hub`-Block der `slides.yaml`. zh-tram-flow migriert (Output byte-identisch verifiziert).

**Repro-Fix (P3):** pip-Extra `[dan]`/`[dsc]` → `[da]` (DE erbt DA-Struktur, kein ML-Extra) — pyproject,
README, Makefile.

**SVG-Pfad-Klärung:** `../img/` in den Views ist deployment-korrekt (klemmt bei GitHub Pages mit
`public/` als Site-Root am Root fest) — lokal via `file://` 404, wie bei zh-tram-flow. Kein Bug.

**Nächster Schritt:** Deployment (`public/` → GitHub Pages) + stale „21→8" im `00_introduction` fixen.
Offene Toolchain-Nachzüge: P1 (ETL-Check-Dimension in project-review) + P4 (Notebook-Header in scaffolding).

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

### 2026-07-13 — Styleguide v2 ausgerollt + vollständiger Storyview-Review

Design-Overhaul der Präsentationen (Skill-seitig in `wgnd-skills/project-case`, Branch
`feature/styleguide-v2`, noch **nicht** nach `main` gemerged/gepusht): 12-Spalten-Raster,
L1–L7-Layouts, E1–E17-Elemente, fixe Kopf-/Content-Zone pro Slide (behebt "Content springt
je Slide"). Titel-Slide-Typografie an den Hub angeglichen (Font/Größe wie `index.html`
Header), Titel/Subline werden jetzt automatisch aus `hub.tagline`/`hub.subtitle` generiert
statt pro View von Hand gepflegt (view-übergreifender Text-Drift damit strukturell
ausgeschlossen).

**Kay hat die Storyview komplett Folie für Folie durchgesehen** (23 Slides) und Design +
Inhalt freigegeben ("für mich sind wir einen richtigen Schritt nach vorn"). Umgesetzte
Änderungen (alle in `public/md/slides.yaml`, Details siehe Git-Log):
- Titel-Slide: L6-Layout-Experiment (zweispaltig: Titel/Subline/Teaser/Start links, KPI-Row
  rechts) — bewusst nur hier aktiv, nicht global ausgerollt.
- Sechs Text-Slides (Genese/Motivation/Ausgangssituation/Aufgabe/Anreicherung/Left-Join) auf
  `layout: callout` umgestellt — volle Breite statt zweispaltigem Fließtext, neue Titel/Texte
  auf 3 davon.
- Datenstrategie-Slide: Bild großformatig zentriert statt Bild-rechts-Layout.
- KPI-Reihen zentrieren jetzt korrekt auch bei <4 Werten (war strukturell links-lastig).
- Closing-Slide: Titel/Subline identisch zur Opening-Titel-Slide (aus Hub generiert), eigener
  Content-Text bleibt handgepflegt (zwei Absätze).
- Vier Anreicherungs-Quellen-Slides (GTFS/Meteo/Events/Geo) zeigen jetzt eine Prozesspfeil-
  Navigationsleiste mit dem jeweils aktuellen Schritt hervorgehoben.
- Agenda-Slide (alle 3 Views einheitlich): Kicker "Agenda", Titel "Übersicht", Liste horizontal
  + vertikal zentriert (`layout: L1`).

**Reale Bugs gefunden und gefixt** (nicht nur Geschmacksfragen): `.reveal` erbte nie die
System-Font — Reveal.js' Theme setzte eine spezifischere Regel direkt auf die Heading-Tags,
wodurch `font-weight:100` zwar im CSS stand, aber mangels geladenem Thin-Schnitt optisch
wirkungslos blieb. Blockquote-Abstand nach KPI-Row/Tabelle/Steps/Empfehlungen: `.content-zone`
ist ein Flex-Container, dort kollabieren Nachbar-Margins nicht wie im normalen Blockfluss —
naive Fixes summierten sich, korrekte Lösung ist eine gezielte Vorgänger-Selektor-Liste.
`--bg-table-alt` war beim früheren Beige→Blau-Grau-Theme-Wechsel übersehen worden (Tabellen
liefen weiter beige).

**Nächster Schritt:** Kay reviewed overview + techview eigenständig (storyview ist fertig,
die anderen beiden Views haben viele Fixes über geteilte Slide-IDs und globales CSS bereits
automatisch geerbt, aber noch keinen eigenen dedizierten Blick bekommen). Danach Entscheidung,
ob `wgnd-skills`-Branch `feature/styleguide-v2` nach `main` gemerged wird (betrifft auch
zh-tram-flow, das dieselben globalen Fixes bereits übernommen hat).

---

### 2026-07-13 (Fortsetzung) — Overview + Techview reviewed, Review-Zyklus abgeschlossen

Kay hat overview und techview ebenfalls Folie für Folie durchgesehen und freigegeben ("für
mich ist das fein") — damit sind alle 3 Views vollständig reviewed. Wesentliche Ergänzungen
gegenüber der Storyview (Details siehe Git-Log, nicht hier dupliziert): Titel-Slide-L6 auch für
overview/techview aktiviert; Genese-Einstiegsslide ("Data Science Abschlussarbeit") war in
overview komplett übersprungen worden — nachgezogen; die fehlende Zürich-Begründung (storyview
hat dafür eine eigene Slide, overview nicht) als vierter Abschnitt in "Der Projektrahmen"
eingefaltet statt eines zusätzlichen Slides (bewusste Entscheidung: overview soll knapp bei
8 Minuten Laufzeit bleiben); techview hatte gar kein Closing (kein "ende"-Kapitel in der
View-Komposition) — ergänzt; Agenda-Titel über alle 3 Views auf "Inhaltsübersicht"
vereinheitlicht.

**Zwei weitere reale Bugs gefunden:** (1) Titel-Slide-KPI-Row brach bei 4 Werten mit langen
Labels "greedy" um (3 in Zeile 1, 1 in Zeile 2 statt sauberem 2×2) — von Flex-Wrap auf CSS-Grid
mit `auto-fit`/`minmax` umgestellt, dabei zusätzlich `width:100%` nötig (der Grid-Container hatte
als Flex-Kind sonst keine echte Breite, gegen die `auto-fit` rechnen konnte). (2) `.pf-grid`
(Karten-Reihe) gefolgt von Fließtext hatte nicht die sonst übliche 3em-Abstandsregel — ergänzt.

`templates/styleguide.html` (wgnd-skills) im gleichen Zug vervollständigt: Titel-L6-Variante,
beide Agenda-Varianten (L1/L6), gestapelte Statement-Callouts, Process-Arrows-Hervorhebung,
und die Abstände-Tabelle korrigiert (die pauschale "40px"-Zeile war seit dem 3em-Fix falsch).

**Aufräum-Pass:** README-Status-Badge war stale ("Phase 1 complete" trotz Phase-3-Arbeit) →
"Phase 2 complete" (Phase 3 hat mit Deployment noch einen echten offenen Punkt). Reports-&-
Artifacts-Sektion im README war bereits korrekt (alle 4 Views verlinkt), keine Änderung nötig.
`public/archive/` ist bereits gitignored (rein lokale Snapshots vom `archive_portfolio_artifacts.py`-
Schritt) — kein Repo-Hygiene-Thema.

**Nächster Schritt:** `wgnd-skills`-Branch `feature/styleguide-v2` (46 Commits vor `main`) mergen
— danach Deployment (`public/` → GitHub Pages, letzter offener Punkt in Phase 3) und/oder
Styleguide-v2-Retrofit auf zh-tram-flow (bestehende Story bleibt, gezielt neue Elemente wie
`box_grid`/`process_arrows`/`layout: callout` dort ergänzen wo passend).

---

### 2026-07-13 (Fortsetzung) — Deployment: GitHub Pages live, Phase 3 abgeschlossen

`git push` (35 Commits) nach `origin/main` — dabei ein kleines Remote-Divergenz (Kay hatte über
die GitHub-Weboberfläche testweise eine `CNAME`-Datei angelegt und wieder gelöscht) sauber
gemerged, kein Konfliktinhalt.

**Deployment-Bug gefunden und gefixt:** GitHub Pages' "Deploy from a branch" bietet nur `/`
(root) oder `/docs` als Ordner an — `/public` lässt sich darüber gar nicht auswählen. Ohne
diese Option lief Pages bislang von Repo-Root mit Jekyll-Verarbeitung: `index.html` zeigte
Jekyll's automatisch aus der README gebautes Theme, `overview`/`storyview`/`techview.html`
gaben 404 (existieren nur unter `public/`). **Betrifft `zh-tram-flow` identisch** (gleicher
Test, gleiches Ergebnis) — keine zh-tram-data-spezifische Macke, sondern eine Lücke zwischen
`DEPLOYMENT.md`-Doku ("Folder: /public") und der tatsächlich über die GitHub-UI wählbaren
Optionen.

Fix: `.github/workflows/pages.yml` (GitHub-Actions-Deployment statt "Deploy from a branch") +
`public/.nojekyll` ergänzt — der Workflow published `public/` direkt als Pages-Artefakt,
unabhängig vom Ordnernamen. Kay musste dazu einmalig in den Repo-Settings die Pages-Source auf
"GitHub Actions" umstellen und den Workflow einmal manuell auslösen (Settings-Wechsel allein
triggert noch keinen Lauf). Danach alle vier Seiten + CSS/Bilder mit 200 verifiziert:
https://kaywiegand.github.io/zh-tram-data/

**README-Links korrigiert:** zeigten auf `public/index.html` etc. (relative Repo-Pfade —
auf GitHub sieht man da nur die Rohdatei, keine gerenderte Seite). Jetzt auf die echten
Pages-URLs umgestellt (`https://kaywiegand.github.io/zh-tram-data/...`), an beiden Stellen
("Where to start" + "Reports & Artifacts"). README bleibt bewusst der Einstiegspunkt für
GitHub-Browser — die Pages-Site ist das eigentliche, gestylte Artefakt.

`docs/PROJECTS.md` (Workspace) und `ROADMAP.md` (Phase 3 jetzt komplett) aktualisiert.

**Nächster Schritt:** `wgnd-skills`-Branch `feature/styleguide-v2` mergen (unverändert offen).
Gleicher Pages-Fix (`.nojekyll` + Actions-Workflow) liegt für `zh-tram-flow` schon lokal
committed bereit, noch nicht gepusht — auf Kays Go warten.

---
