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

### Ausgangssituation

# Zurich Tram Data

**Ein sauberer Datensatz aus fünf Quellen**
**Die Data-Engineering-Grundlage für zh-tram-flow**

* **38 GB** — IST-Rohdaten, schweizweit
* **94,4 M** — Halt-Ereignisse im Master
* **26** — Spalten aus 5 Quellen
* **9** — reproduzierbare Notebooks

## Inhalt
*Diese Präsentation auf einen Blick*

1. Das Projekt
2. Reduktion
3. Anreicherung
4. Der Master
5. Grenzen & Einordnung

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

## Die Datenstrategie auf einen Blick
*Fünf Quellen, ein Weg zum Master*



---

### Reduktion

## Das Überwältigende bändigen
*Reduktion in drei Schritten*



---

### Anreicherung

## Das Dünne aufwerten
*Vier Quellen, ein bemerkenswerter Sonderfall*

* **Vier Quellen angereichert**
  - GTFS Fahrplan (+3) · Meteo Wetter (+7) · Geo Stadtkreis (+2) · Events (+4)
  - 10 → 26 Spalten
* **Spotlight: Events**
  - Keine Open-Data-Quelle → von Hand recherchiert und aufgebaut
  - Der Fall, der echten Daten-Spürsinn verlangt


---

### Vereinigung

## Die Join-Pipeline
*Vier Quellen, drei Joins, eine Qualitätsprüfung*



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

## Einordnung
*Das Fundament und der Aufbau*

> zh-tram-data ist das Data-Engineering-Fundament: der saubere, reproduzierbare Master-Datensatz.
> Analyse, Modellierung und Vorhersage bauen darauf auf — in zh-tram-flow. Zusammen der volle Data-Cycle, sauber in Fundament und Aufbau getrennt.
