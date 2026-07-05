# Portfolio Summary — Zurich Tram Data
<!-- Interface-Datei: Von /project-case story befüllt.
     Zahlenquelle für /project-case report und slides.
     DE-Case (engineering-first): "Key Findings" → "Engineering Decisions",
     "Model Results" → "Data Quality & Pipeline", "Recommendations" → "Known Limitations".
     Alle Zahlen aus Notebooks / echtem Master-Parquet / PROCESS_LOG — nichts erfunden.
-->

---

## Project

```
name:       Zurich Tram Data
slug:       zh-tram-data
type:       DE
stage:      Phase 1 abgeschlossen — Master reproduziert, Portfolio-Aufbereitung läuft
target:     vbz_master.parquet (ein sauberer, angereicherter Master-Datensatz)
stack:      Python · Polars · GeoPandas · Shapely · Plotly · Jupyter · uv
period:     2023–2025 (IST-Format v1)
rows:       94.358.531 Halt-Ereignisse × 26 Spalten
notebooks:  9 (00–08)
decisions:  6 dokumentierte Engineering-Entscheidungen
sources:    5 (IST · GTFS · Meteo · Events · Geo)
```

---

## Storyline

```
thesis:     Reduzieren was da ist, anreichern was fehlt — aus 38 GB schweizweiten Rohdaten
            wird mit den richtigen Werkzeugen und begründeten Entscheidungen das Relevante
            herausgefiltert und durch gezielt recherchierte Zusatzquellen zu einem sauberen,
            reproduzierbaren Master-Datensatz vereint, mit dem man wirklich arbeiten kann.
hook:       Für Zürcher Events gibt es keine strukturierte Open-Data-Quelle — die Anreicherung
            musste hier von Hand recherchiert und aufgebaut werden.
proof:      Zwei Bögen — Reduktion (38 GB → VBZ Tram) und Anreicherung (10 → 26 Spalten aus
            fünf Quellen), jede Entscheidung im Notebook begründet, Master 1:1 reproduzierbar.
so_what:    Die eigentliche Data-Science-Arbeit beginnt oft nicht beim Modell, sondern beim
            Datensatz — der Weg dorthin ist der Differenzierer.
```

---

## Data Challenge
<!-- Ersetzt "Problem" — kein KPI-Gap, sondern die Datenlage -->

```
challenge_1: Skala — IST-Rohdaten sind 38 GB komprimiert und beschreiben den gesamten
             öffentlichen Verkehr der Schweiz (~400 Transportunternehmen). Relevant ist nur
             ein schmaler Ausschnitt: VBZ Tram Zürich.
challenge_2: Fragmentierung — Verspätung wird erst durch Kontext erklärbar (Fahrplan, Wetter,
             Events, Geografie). Diese Quellen liegen in unterschiedlichen Formaten, Auflösungen
             und Lizenzen vor — teils gibt es gar keine strukturierte Quelle.
challenge_3: Kein fertiger Datensatz — für die Zürcher Tram-Realität existiert kein einzelner
             analysefähiger Datensatz. Er musste gebaut werden.
problem_statement: |
  Es gibt keinen fertigen Datensatz, der die realen Tram-Halte der VBZ mit ihrem Kontext
  verbindet. Die Rohdaten sind zu groß und zu breit (schweizweit), der Kontext zu verstreut
  (fünf heterogene Quellen). Ziel ist ein einziger, sauberer, reproduzierbarer Master —
  die Data-Engineering-Grundlage für zh-tram-flow (Analyse & Verspätungsvorhersage).
```

---

## Engineering Decisions
<!-- Ersetzt "Key Findings". Zwei Bögen: A = Reduktion, B = Anreicherung. -->

### Bogen A — Reduktion (das Überwältigende bändigen)

### D1 — Filter: Von der Schweiz zu VBZ Tram
```
decision:  Rohdaten schweizweit → VBZ Tram Zürich über begründete Filterkette
number:    ~400 Transportunternehmen → 1 (BETREIBER_ID = 85:3849), PRODUKT_ID = Tram
detail:    Nur REAL-Messungen (echte GPS), keine Durchfahrten/Zusatzfahrten — Ausfälle
           (FAELLT_AUS_TF) bewusst behalten als extremster Verspätungsfall. ~11 % Zeilen entfernt.
source:    00_introduction · 02_ingestion-ist
```

### D2 — Werkzeugwahl: Polars statt Pandas
```
decision:  Benchmark auf dem realen IST-Datensatz entscheidet die Werkzeugwahl
number:    Ladezeit 25,7 s → 6,6 s · RAM 6,1 GB → ~1,4 GB (je ~4×)
detail:    Polars für alle großen Operationen (IST, Merge); Pandas für kleine Quellen
           (GTFS/Meteo/Events) und als Lernreferenz. Bewusste, gemessene Entscheidung.
source:    01_tooling-evaluation · 00_introduction
```

### D3 — Spalten- und Scope-Reduktion
```
decision:  21 IST-Rohfelder auf 10 reduziert, Scope auf 2023–2025 / Format v1 begrenzt
number:    21 → 10 Spalten (KEEP_COLS) · Format-Wechsel v2 ab Mitte 2025 bewusst ausgeklammert
detail:    Nach Filter konstante Felder (Betreiber, Produkt) und technische IDs verworfen;
           Delays und stop_sequence abgeleitet. ~1.035 Tages-Parquets statt einer Großdatei —
           einzelne Tage nachladbar/ersetzbar, per scan_parquet('*.parquet') als ein Datensatz.
source:    02_ingestion-ist · 00_introduction
```

### Bogen B — Anreicherung (das Dünne aufwerten)

### D4 — Quellen identifizieren und recherchieren
```
decision:  Vier Kontextquellen bestimmt, die Tram-Verspätung erklärbar machen
number:    5 Quellen gesamt — IST · GTFS · Meteo · Events · Geo
detail:    Systematische Sichtung der Zürcher Open-Data-Landschaft; jede Quelle mit eigener
           Herausforderung (Format, Auflösung, Lizenz). Auswahl nach Analyserelevanz, nicht
           nach Verfügbarkeit.
source:    00_introduction · 03–06
```

### D5 — Der harte Fall Events: kein Open Data → manueller Aufbau
```
decision:  Ohne strukturierte Quelle wird der Event-Kalender von Hand recherchiert und gebaut
number:    Schwellenwert > 1.000 Besucher · Stadt Zürich · 2023–2025
detail:    Keine maschinenlesbare Quelle für Zürcher Events verfügbar — Crawl via Gemini,
           Perplexity, Transfermarkt (FCZ/GC-Spiele, Street Parade, Züri Fäscht …). Eine echte
           Engineering-/Recherche-Entscheidung, kein Nebenschauplatz.
source:    05_ingestion-events · 00_introduction
```

### D6 — Vereinigung: heterogene Quellen zu einem Master
```
decision:  Left Joins über alle Quellen, Spatial Join für Geografie → ein Master-Datensatz
number:    10 → 26 Spalten (+3 GTFS, +2 Geo, +7 Meteo, +4 Events)
detail:    Left Join überall (kein Datenverlust — fehlende Werte werden null); Meteo aus 3
           Quellen (UGZ/Wapo/ERZ) auf stündliches Raster konsolidiert, floor(1h) als Schlüssel;
           Stadtkreis via Punkt-in-Polygon-Spatial-Join. Datetime-Precision-Bug (ns vs. us) beim
           Meteo-Join gefunden und gefixt.
source:    07_master-preparation · 03_ingestion-gtfs · 04_ingestion-meteo · 06_geo-reference
```

---

## Data Quality & Pipeline
<!-- Ersetzt "Model Results" — kein ML. Der Master und seine Validierung sind das Ergebnis. -->

```
master_file:    data/interim/vbz_master.parquet
rows:           94.358.531 Halt-Ereignisse (eine Zeile pro Halt, ~230 Halte je Fahrt)
columns:        26 (verifiziert am Parquet-Schema)
composition:    10 IST · 3 GTFS · 2 Geo · 7 Meteo · 4 Events (Geo = Stadtkreis via Spatial Join)
reproducible:   1:1 über 9 nummerierte Notebooks (00–08), deckungsgleich mit dem
                ursprünglichen Referenz-Datensatz
join_strategy:  Left Join (kein Zeilenverlust) + Spatial Join (Stadtkreis)
validation:     08_master-validation — Zeilen-/Spaltenzahl, Schema, Null-Verteilung geprüft
```

### Pipeline (Data Cycle)

| Schritt | Notebook | Ergebnis |
|---|---|---|
| Bestandsaufnahme & Strategie | 00_introduction | Datenlandschaft + alle Entscheidungen |
| Werkzeugwahl | 01_tooling-evaluation | Polars (begründet per Benchmark) |
| Ingestion IST | 02_ingestion-ist | gefilterte, reduzierte Halt-Ereignisse |
| Ingestion GTFS | 03_ingestion-gtfs | Fahrplan + Stadtkreis-Lookup |
| Ingestion Meteo | 04_ingestion-meteo | stündlich konsolidiertes Wetter |
| Ingestion Events | 05_ingestion-events | manuell recherchierter Event-Kalender |
| Geo-Referenz | 06_geo-reference | Bibliotheks-Benchmark + Stadtkreis-Zuordnung |
| Vereinigung | 07_master-preparation | Join → vbz_master.parquet (26 Spalten) |
| Validierung | 08_master-validation | reproduzierter, geprüfter Master |

---

## Figures
<!-- DE-Case: Prozessdiagramme statt Analyse-Charts. Beide als SVG. -->

```yaml
pipeline:
  - img/vbz_strategy.svg       # Gesamte Datenpipeline: 5 Quellen → Merge → vbz_master.parquet
  - img/vbz_preparation.svg    # Master-Preparation: 4 Quellen → 3 Joins → Qualitätsprüfung → Master
```

---

## Known Limitations & Next Iteration
<!-- Ersetzt "Recommendations". Transparenz über Grenzen ist ein DE-Portfolio-Signal. -->

```
l1:
  title:  trip_id ↔ GTFS nicht direkt matchbar
  detail: IST-FAHRT_BEZEICHNER (85:3849:…) und GTFS-trip_id (1.T0.1-10-…) haben 0 % Overlap.
          Richtungsspezifische Analysen und Kaskadeneffekt (prev_trip_delay) brauchen eine
          Umlauf-basierte Brücke. Bewusst offen (BACKLOG #1) — Kandidat für Projektneuauflage.

l2:
  title:  UMLAUF_ID beim Reduktions-Schritt verworfen
  detail: KEEP_COLS behält 10 von 21 Feldern; UMLAUF_ID (Fahrzeug-/Umlauf-Kennung) wäre die
          direktere Brücke für Kaskadenanalyse. Nachträgliches Hinzufügen = volles Reprocessing
          ab den Roh-ZIPs. Dokumentierte Grenze (BACKLOG #2), nicht in dieser Iteration.

l3:
  title:  Format v2 ab Mitte 2025 ausgeklammert
  detail: Scope bleibt bei v1 (2023–2025) für Schema-Einheitlichkeit. 2026 + v2 = spätere Iteration.

l4:
  title:  Meteo auf zwei Referenzstationen begrenzt
  detail: Stampfenbachstrasse + Mythenquai decken Stadt- vs. Seelage ab — bewusster MVP-Umfang,
          erweiterbar um weitere Stationen.
```

---

## Status

```
generated_by:   /project-case story
generated_at:   2026-07-03
summary_version: 1
portfolio_check: ⚠️ partial (DE-Case, engineering-first)
report_html:    ✅ generated (index + overview/storyview/techview)
slides_html:    ✅ generated (aus slides.yaml, 6 Kapitel / 29 Slide-Einträge)
dashboard:      ❌ not deployed (DE-Case — kein Dashboard vorgesehen)
open_finding:   00_introduction sagt IST-Reduktion "21 → 8"; korrekt ist "21 → 10" (KEEP_COLS,
                verifiziert). Notebook-Text nachziehen (mit Kay abstimmen).
```
