# Zurich Tram Data

**Projekt:** Zurich Tram Data
**Beschreibung:** Der Datensatz & sein Weg
**Autor:** Kay Wiegand
**Zielgruppe:** HR · Business · Hiring Manager
**Dauer:** 8 Minuten
**Zeitraum:** 2023–2025
**GitHub:** [kaywiegand/zh-tram-data](https://github.com/kaywiegand/zh-tram-data)

---


---

### Title

# Zurich Tram Data

**Ein sauberer Datensatz aus fünf Quellen**
**Die Data-Engineering-Grundlage für zh-tram-flow**

* **38 GB** — IST-Rohdaten, schweizweit
* **94,4 M** — Halt-Ereignisse im Master
* **26** — Spalten aus 5 Quellen
* **9** — reproduzierbare Notebooks


---

### Inhalt

## Inhalt
*Diese Präsentation auf einen Blick*

1. Genese & Motivation
2. Ausgangssituation
3. Daten Reduktion
4. Daten Anreicherung
5. Daten Zusammenführung
6. Masterdatensatz als Resultat
7. Limitierungen


---

### Genese & Motivation

## Persönliche Motivation
*Ein datengetriebenes Thema mit gesellschaftlicher Relevanz*

> Daten sollen sinnstiftend eingesetzt werden — mit greifbarem Bezug zum Alltag, zur Lebensqualität, im besten Fall zur Nachhaltigkeit.
> Öffentlicher Verkehr trifft das genau: täglich erlebbar, gesellschaftlich relevant, datenreich. Die Recherche führte über den ÖPNV nach Zürich.


---

### Ausgangssituation

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

## Die Datenstrategie
*Fünf Datenquellen, ein reproduzierbarer Master-Datensatz*



---

### Daten Reduktion

## Das Überwältigende bändigen
*Reduktion in drei Schritten*



---

### Daten Anreicherung

## Das Dünne aufwerten
*Vier Quellen, ein bemerkenswerter Sonderfall*

* **Vier Quellen angereichert**
  - GTFS Fahrplan (+3) · Meteo Wetter (+7) · Geo Stadtkreis (+2) · Events (+4)
  - 10 → 26 Spalten
* **Spotlight: Events**
  - Keine Open-Data-Quelle → von Hand recherchiert und aufgebaut
  - Der Fall, der echten Daten-Spürsinn verlangt


---

### Daten Zusammenführung

## Die Join-Pipeline
*Vier Quellen über drei Joins zum validierten Master*



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

### Ende

## Zurich Tram Data
*Recherche · Reduktion · Anreicherung · Vereinigung*

> Data-Engineering-Fundament für das Analyse-Projekt zh-tram-flow
