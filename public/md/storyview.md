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

### Title

# Zurich Tram Data

**Vom Rohdaten-Archiv zum reproduzierbaren Master-Datensatz**
**Recherche · Reduktion · Anreicherung · Vereinigung**

* **38 GB** — IST-Rohdaten, schweizweit
* **94,4 M** — Halt-Ereignisse im Master
* **26** — Spalten aus 5 Quellen
* **9** — reproduzierbare Notebooks


---

### Inhalt

## Inhalt
*Sieben Kapitel entlang des Data-Engineering-Zyklus*

1. Genese & Motivation
2. Ausgangssituation
3. Daten Reduktion
4. Daten Anreicherung
5. Daten Zusammenführung
6. Masterdatensatz als Resultat
7. Limitierungen
8. Ausblick


---

### Genese & Motivation

## Die Genese
*Ausgangspunkt und Themenfindung des Projekts*

> Entstanden als Abschlussarbeit einer Data-Science-Fortbildung — der Rahmen war bewusst offen: nicht welches Modell, sondern welches Thema.
> Gesucht war ein Gegenstand, an dem sich Data Science nicht abstrakt anfühlt, sondern an einem Alltagsbeispiel mit echtem Impact nachvollziehbar wird.

## Persönliche Motivation
*Ein datengetriebenes Thema mit gesellschaftlicher Relevanz*

> Daten sollen sinnstiftend eingesetzt werden — mit greifbarem Bezug zum Alltag, zur Lebensqualität, im besten Fall zur Nachhaltigkeit.
> Öffentlicher Verkehr trifft das genau: täglich erlebbar, gesellschaftlich relevant, datenreich. Die Recherche führte über den ÖPNV nach Zürich.


---

### Ausgangssituation

## Warum Zürich
*Zürichs Open-Data-Ökosystem als Grundlage für reproduzierbare Analysen*

> Zürich betreibt eine außergewöhnlich gute Open-Data-Landschaft für sein Tramnetz (VBZ) — frei zugänglich, gut dokumentiert, granular genug für echte Analyse.
> Auch die Recherche nach ergänzenden Zürcher Datenquellen (Wetter, Events, Geografie) war vielversprechend. Das war der Startpunkt des Projekts.

## Der Projektrahmen
*Zielsetzung, Scope und Einordnung im Data-Lifecycle*

* **Ziel**
  - Ein einziger, sauberer Master-Datensatz der realen VBZ-Tram-Halte
  - Angereichert mit Fahrplan, Wetter, Events und Geografie
* **Fokus**
  - Der Weg dorthin: Recherche · Filterung · Zusammenführung · Qualitätssicherung
  - Bewusst nicht Modellierung
* **Einordnung**
  - Data-Engineering-Grundlage für zh-tram-flow (Analyse & Verspätungsvorhersage)

## Die Aufgabe
*Aufbau einer integrierten, analysefähigen Datengrundlage*

> Einen Datensatz bauen, mit dem eine sinnvolle, qualitativ belastbare Analyse des Zürcher Tramnetzes überhaupt erst möglich wird.
> Der Leitgedanke dahinter: reduzieren was da ist, anreichern was fehlt.

## Die Datenstrategie
*Fünf Datenquellen, ein reproduzierbarer Master-Datensatz*



---

### Daten Reduktion

## Schweiz ÖPNV IST-Daten
*38 GB schweizweite Ist-Daten als Ausgangsvolumen*

* **38 GB** — komprimierte Archiv-ZIPs
* **~400** — Transportunternehmen CH
* **5** — Verkehrsmittel-Arten
> Die IST-Rohdaten beschreiben den gesamten öffentlichen Verkehr der Schweiz — jeder Zug, Bus, jedes Tram, Schiff, jede Seilbahn. Relevant ist ein schmaler Ausschnitt: VBZ Tram Zürich.

## Polars statt Pandas
*Werkzeugwahl per Benchmark auf dem realen Datenvolumen*

> Entscheidung: Polars für alle großen Operationen (IST, Merge). Pandas bleibt für kleine Quellen (GTFS/Meteo/Events) und als Lernreferenz.

## Auf VBZ Tram
*Regelbasierte Filterung von ~400 Betreibern auf das VBZ-Tramnetz*

> ~11 % der Zeilen entfernt — übrig bleiben echte, planmäßige Halte mit GPS-Zeitstempeln, plus alle Ausfälle.


---

### Daten Anreicherung

## Warum anreichern
*Kontextdaten machen Verspätung erst erklärbar*

> Ein Tram-Halt mit einer Verspätungszahl erklärt für sich genommen wenig. Erst der Kontext — Fahrplan, Wetter, Events, Geografie — macht Verspätung nachvollziehbar.
> Also: vier gezielt recherchierte Zusatzquellen identifizieren und in den Master integrieren.

## Fahrplan (GTFS)
*Soll-Fahrplan und Haltestellen-Stammdaten aus dem ZVV-Netz*

* **Woher**
  - data.stadt-zuerich.ch · ZIP/TXT · CC0
  - 3 Jahrgänge, gesamtes ZVV-Netz
* **Was zu tun**
  - Auf VBZ-Tram-Linien filtern, 2024 als Primärreferenz
  - 10+ GTFS-Tabellen → 4 Parquets (routes, stops, shapes, trips)
* **Wie übernommen**
  - Join über bpuic (Haltestellen-ID) → stop_name, stop_lat, stop_lon
  - +3 Spalten im Master

## Wetter (Meteo)
*Drei heterogene Quellen, konsolidiert auf Stundenbasis*

* **Woher**
  - data.stadt-zuerich.ch (UGZ, Wapo, ERZ) · CSV/Parquet · CC0
  - 3 Quellen, unterschiedliche Auflösung
* **Was zu tun**
  - Auf ein stündliches Raster konsolidieren
  - 2 Referenzstationen: Stampfenbachstrasse (Stadtlage) + Mythenquai (Seelage)
* **Wie übernommen**
  - floor(1h) als Join-Schlüssel zu den Tram-Zeitstempeln
  - +7 Spalten (u.a. temperature, precipitation, wind_speed, flood_intensity)

## Events nach Größe
*Fehlende Open-Data-Quelle durch eigene Recherche geschlossen*

* **Woher**
  - Keine strukturierte Open-Data-Quelle verfügbar
  - Manueller Crawl: Gemini, Perplexity, Transfermarkt
* **Was zu tun**
  - Schwellenwert > 1.000 Besucher, Stadt Zürich, 2023–2025
  - FCZ/GC-Spiele, Street Parade, Züri Fäscht …
* **Wie übernommen**
  - Als CSV aufgebaut, Join über das Datum
  - +4 Spalten (event_name, event_type, event_size, event_location)

## Stadtkreise (Geo)
*Räumliche Zuordnung der Haltestellen per Spatial Join*

* **Woher**
  - data.stadt-zuerich.ch · GeoJSON · CC0
  - Stadtkreis-Grenzen, sofort verwendbar
* **Was zu tun**
  - Jeder Haltestelle ihren Stadtkreis zuordnen
* **Wie übernommen**
  - Spatial Join (Punkt-in-Polygon) auf die GTFS-Stops → district_nr, district_name
  - +2 Spalten — bereits im Master, kein nachträglicher Join in der EDA nötig


---

### Daten Zusammenführung

## Die Join-Pipeline
*Vier Quellen über drei Joins zum validierten Master*


## Left Join als Standard
*Vollständigkeitserhalt: Fehlwerte als null statt Zeilenverlust*

> Left Join überall: jede Tram-Fahrt bleibt erhalten. Fehlende Werte (Sensor-Ausfall, Event-freier Tag) werden null — statt die Zeile zu löschen.
> Datenverlust durch Join ist der häufigste stille Bug in Merge-Pipelines. Left Join macht ihn unmöglich.

## Zeitstempel als Herausforderung
*Datentyp- und Zeitraster-Fallstricke beim Zusammenführen*



---

### Masterdatensatz als Resultat

## Der Master-Datensatz
*Analysefertige, reproduzierbare Datengrundlage*

* **94,4 M** — Halt-Ereignisse
* **26** — Spalten aus 5 Quellen
* **9** — Notebooks, 00–08
* **100 %** — reproduzierbar
> vbz_master.parquet — eine Zeile pro Halt (~230 je Fahrt), angereichert mit Fahrplan, Wetter, Events und Stadtkreis. 1:1 reproduzierbar über die 9 Notebooks.


---

### Limitierungen

## Bewusste Limitierung
*Dokumentierte Scope-Entscheidungen dieser Ausbaustufe*

> Bewusst dokumentierte Grenzen, nicht übersehene Fehler. Transparenz über Known Issues gehört zu sauberem Data Engineering.


---

### Ausblick

## Weitere Perspektiven
*Erweiterungen für eine nächste Iteration*



---

### Ende

## Zurich Tram Data
*Recherche · Reduktion · Anreicherung · Vereinigung*

> Data-Engineering-Fundament für das Analyse-Projekt zh-tram-flow
