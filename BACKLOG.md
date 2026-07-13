# BACKLOG.md – Zurich Tram Data

Projektspezifische offene Tasks und Todos.
Nie mitten in einer Session den Kontext wechseln — hier notieren, gesammelt abarbeiten.

Prio: `1` = hoch · `2` = mittel · `3` = niedrig

---

## Aktive Tasks

| # | Beschreibung | Prio |
| :--- | :--- | :--: |
| B | **Deployment** (`public/` → GitHub Pages) — letzter offene Punkt in Phase 3, siehe `ROADMAP.md`. | 1 |

> Die früheren Migrations-Findings #1 (trip_id-Brücke) und #2 (`UMLAUF_ID`) sind keine offenen
> Tasks, sondern Scope-Grenzen dieser Auflage — nach unten in die OP-Sektion umgezogen (siehe unten).

---

## Erledigt ✅

| # | Beschreibung | Erledigt |
| :--- | :--- | :--- |
| A | Public-Inhalte kontrollieren + abstimmen (Portfolio-Layer) — alle 3 Views (`overview`/`storyview`/`techview`) Folie für Folie durchgesehen und freigegeben. | ✅ 2026-07-13 — Styleguide v2, siehe `PROCESS_LOG.md` |

---

## 🔬 Research Opportunities & Future Reprocessing (OP)

Systematische Erweiterungsmöglichkeiten, die **nicht** in dieser Auflage umgesetzt werden.
Gemeinsame Klammer: alle setzen ein **volles Reprocessing ab den Roh-ZIPs** voraus (liegen nur
auf externer Platte, nicht im Repo). Sie sind bewusste Scope-Grenzen der v1 — kein offener
Task, kein Blocker. Erst bei einer Neuauflage / v2 relevant, dann gesammelt vor dem
Neu-Schreiben der IST-Parquets entscheiden.

| OP # | Beobachtung | Prio | Voraussetzung | Entdeckt in |
| :--- | :--- | :--: | :--- | :--- |
| **OP-1** | **trip_id IST↔GTFS nicht direkt matchbar** — IST-`FAHRT_BEZEICHNER` (`85:3849:…`) vs. GTFS-`trip_id` (`1.T0.1-10-P-j23-…`) → 0 % String-Overlap. War Grund für die Entfernung des Fahrtrichtungs-Filters im zh-tram-flow-Dashboard (#67b). Voraussetzung für richtungsspezifische Analysen und für `prev_trip_delay`/Kaskadeneffekt (F-NET-07). Prüfrichtung: fahrplanbasierte Brücke über `LINIEN_TEXT` + `ANKUNFTSZEIT` + `BPUIC`-Sequenz. | 1 | Fachplan-Bridge, kein Reprocessing zwingend — aber gemeinsam mit OP-2 zu klären | zh-tram-flow `PROCESS_LOG.md:1727`, 2026-06-25 |
| **OP-2** | **Verworfene Rohspalten beim IST-Processing** — `KEEP_COLS` in `02_ingestion-ist.ipynb` behält 10 Spalten. Dauerhaft verloren: `UMLAUF_ID` (Fahrzeug-/Umlauf-Kennung — evtl. die *direktere* Brücke für Kaskaden-Analyse als trip_id-Kontinuität), `AN_PROGNOSE_STATUS`/`AB_PROGNOSE_STATUS` (nur als Filter genutzt), `VERKEHRSMITTEL_TEXT`, `HALTESTELLEN_NAME`, `BETREIBER_ABK`/`BETREIBER_NAME`. | 2 | Volles Reprocessing ab Roh-ZIPs — vor Neu-Schreiben der Parquets entscheiden, ob `UMLAUF_ID` mitkommt | `process_ist_daten.py` + `02_ingestion-ist.ipynb`, Migration 2026-07-02 |

> **Zusammenhang OP-1 ↔ OP-2:** Beide zielen auf denselben blinden Fleck — die fehlende
> Fahrt-/Umlauf-Kontinuität für Kaskadeneffekte. OP-2 (`UMLAUF_ID` aus den Rohdaten) könnte OP-1
> (fahrplanbasierte Brücke) überflüssig machen. Bei einer Neuauflage zuerst OP-2 klären, dann
> entscheiden, ob OP-1 überhaupt noch nötig ist.
