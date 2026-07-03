# Zurich Tram Data

**Projekt:** Zurich Tram Data
**Beschreibung:** Vom Rohdaten-Archiv zum Master
**Autor:** Kay Wiegand
**Zielgruppe:** Portfolio · Vollbild
**Dauer:** 20 Minuten
**Zeitraum:** 2023–2025
**GitHub:** [kaywiegand/zh-tram-data](https://github.com/kaywiegand/zh-tram-data)

---


---

### Ausgangssituation

# Zurich Tram Data

**Vom Rohdaten-Archiv zum Master-Datensatz**
**Recherche · Reduktion · Anreicherung · Vereinigung**

* **38 GB** — IST-Rohdaten, schweizweit
* **94,4 M** — Halt-Ereignisse im Master
* **26** — Spalten aus 5 Quellen
* **9** — reproduzierbare Notebooks

## Inhalt
*Sechs Kapitel, ein durchgehender Datenpfad*

1. Ausgangssituation
2. Reduktion — das Überwältigende bändigen
3. Anreicherung — das Dünne aufwerten
4. Vereinigung zum Master
5. Das Resultat
6. Grenzen & Ausblick

## Worum es geht
*Ziel, Fokus und Einordnung des Projekts*

* **Ziel**
  - Ein einziger, sauberer Master-Datensatz der realen VBZ-Tram-Halte
  - Angereichert mit Fahrplan, Wetter, Events und Geografie
* **Fokus**
  - Der Weg dorthin: Recherche · Filterung · Zusammenführung · Qualitätssicherung
  - Bewusst nicht Modellierung
* **Einordnung**
  - Data-Engineering-Grundlage für zh-tram-flow (Analyse & Verspätungsvorhersage)

## Die These
*Ein Satz, der das Projekt trägt*

> Reduzieren was da ist, anreichern was fehlt.
> Aus 38 GB schweizweiten Rohdaten wird das Relevante herausgefiltert — und die für sich dünnen Tram-Halte durch gezielt recherchierte Zusatzquellen zu einem Datensatz vereint, mit dem man wirklich arbeiten kann.

## Die Datenstrategie auf einen Blick
*Fünf Quellen, ein Weg zum Master*



---

### Reduktion

## Die Ausgangslage: das ganze Land
*38 GB, jede Fahrt der Schweiz*

* **38 GB** — komprimierte Archiv-ZIPs
* **~400** — Transportunternehmen CH
* **5** — Verkehrsmittel-Arten
> Die IST-Rohdaten beschreiben den gesamten öffentlichen Verkehr der Schweiz — jeder Zug, Bus, jedes Tram, Schiff, jede Seilbahn. Relevant ist ein schmaler Ausschnitt: VBZ Tram Zürich.

## Werkzeugwahl: Polars statt Pandas
*Auf den echten Daten gemessen, nicht angenommen*

> Entscheidung: Polars für alle großen Operationen (IST, Merge). Pandas bleibt für kleine Quellen (GTFS/Meteo/Events) und als Lernreferenz.

## Von der Schweiz zu VBZ Tram
*Jede Filter-Entscheidung begründet*

> ~11 % der Zeilen entfernt — übrig bleiben echte, planmäßige Halte mit GPS-Zeitstempeln, plus alle Ausfälle.


---

### Anreicherung

## Tram-Halte allein erklären wenig
*Was macht Verspätung überhaupt nachvollziehbar?*

> Ein Tram-Halt mit einer Verspätungszahl erklärt für sich genommen wenig. Erst der Kontext — Fahrplan, Wetter, Events, Geografie — macht Verspätung nachvollziehbar.
> Also: vier gezielt recherchierte Zusatzquellen identifizieren und in den Master integrieren.

## Anreicherung 1 — GTFS (Fahrplan)
*woher · was zu tun · wie übernommen*

* **Woher**
  - data.stadt-zuerich.ch · ZIP/TXT · CC0
  - 3 Jahrgänge, gesamtes ZVV-Netz
* **Was zu tun**
  - Auf VBZ-Tram-Linien filtern, 2024 als Primärreferenz
  - 10+ GTFS-Tabellen → 4 Parquets (routes, stops, shapes, trips)
* **Wie übernommen**
  - Join über bpuic (Haltestellen-ID) → stop_name, stop_lat, stop_lon
  - +3 Spalten im Master

## Anreicherung 2 — Meteo (Wetter)
*woher · was zu tun · wie übernommen*

* **Woher**
  - data.stadt-zuerich.ch (UGZ, Wapo, ERZ) · CSV/Parquet · CC0
  - 3 Quellen, unterschiedliche Auflösung
* **Was zu tun**
  - Auf ein stündliches Raster konsolidieren
  - 2 Referenzstationen: Stampfenbachstrasse (Stadtlage) + Mythenquai (Seelage)
* **Wie übernommen**
  - floor(1h) als Join-Schlüssel zu den Tram-Zeitstempeln
  - +7 Spalten (u.a. temperature, precipitation, wind_speed, flood_intensity)

## Anreicherung 3 — Events (der harte Fall)
*Kein Open Data — von Hand aufgebaut*

* **Woher**
  - Keine strukturierte Open-Data-Quelle verfügbar
  - Manueller Crawl: Gemini, Perplexity, Transfermarkt
* **Was zu tun**
  - Schwellenwert > 1.000 Besucher, Stadt Zürich, 2023–2025
  - FCZ/GC-Spiele, Street Parade, Züri Fäscht …
* **Wie übernommen**
  - Als CSV aufgebaut, Join über das Datum
  - +4 Spalten (event_name, event_type, event_size, event_location)

## Anreicherung 4 — Geo (Stadtkreise)
*woher · was zu tun · wie übernommen*

* **Woher**
  - data.stadt-zuerich.ch · GeoJSON · CC0
  - Stadtkreis-Grenzen, sofort verwendbar
* **Was zu tun**
  - Jeder Haltestelle ihren Stadtkreis zuordnen
* **Wie übernommen**
  - Spatial Join (Punkt-in-Polygon) auf die GTFS-Stops → district_nr, district_name
  - +2 Spalten — bereits im Master, kein nachträglicher Join in der EDA nötig


---

### Vereinigung

## Die Join-Pipeline
*Vier Quellen, drei Joins, eine Qualitätsprüfung*


## Left Joins — kein Zeilenverlust
*Die wichtigste Join-Entscheidung*

> Left Join überall: jede Tram-Fahrt bleibt erhalten. Fehlende Werte (Sensor-Ausfall, Event-freier Tag) werden null — statt die Zeile zu löschen.
> Datenverlust durch Join ist der häufigste stille Bug in Merge-Pipelines. Left Join macht ihn unmöglich.

## Die Tücken im Detail
*Zwei Stolpersteine beim Join*



---

### Resultat

## Der Master-Datensatz
*Ein Datensatz, mit dem man wirklich arbeiten kann*

* **94,4 M** — Halt-Ereignisse
* **26** — Spalten aus 5 Quellen
* **9** — Notebooks, 00–08
* **100 %** — reproduzierbar
> vbz_master.parquet — eine Zeile pro Halt (~230 je Fahrt), angereichert mit Fahrplan, Wetter, Events und Stadtkreis. 1:1 reproduzierbar über die 9 Notebooks, deckungsgleich mit dem Original aus sf_data-research.


---

### Grenzen & Ausblick

## Grenzen & bewusste Versäumnisse
*Transparenz über Known Issues*

> Bewusst dokumentierte Grenzen, nicht übersehene Fehler. Transparenz über Known Issues gehört zu sauberem Data Engineering.

## Ausblick
*Was eine nächste Iteration angeht*


## Einordnung
*Das Fundament und der Aufbau*

> zh-tram-data ist das Data-Engineering-Fundament: der saubere, reproduzierbare Master-Datensatz.
> Analyse, Modellierung und Vorhersage bauen darauf auf — in zh-tram-flow. Zusammen der volle Data-Cycle, sauber in Fundament und Aufbau getrennt.
