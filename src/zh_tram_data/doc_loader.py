import os
from pathlib import Path
from IPython.display import Markdown, display

# Wir definieren das Projekt-Root-Verzeichnis relativ zu dieser Datei
# doc_loader.py liegt in /src/zh_tram_data/
# .parent ist /src/zh_tram_data/, .parent.parent.parent ist das Root-Verzeichnis (zh-tram-data)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DOC_PATHS = {
    "meteo":        "data/interim/meteo/meteo-master.md",
    "events":       "data/interim/events/events-master.md",
    "ist_daten":    "data/interim/ist-daten/ist-daten.md",
    "gtfs":         "data/interim/gtfs/gtfs.md",

    "geo":          "data/raw/geo/geo.md",
    "event_subs":   "data/raw/events/event-subs.md",
    "gtfs_raw":     "data/raw/gtfs/gtfs.md",
    "meteo_erz":    "data/raw/meteo/erz/erz-ent.md",
    "meteo_wapo":   "data/raw/meteo/wapo/messwerte_wapo.md",
    "meteo_ugz":    "data/raw/meteo/ugz/ugz_ogd_meteo.md",
}

def show_doc(key):
    rel_path = DOC_PATHS.get(key.lower())
    
    if not rel_path:
        print(f"Fehler: Key '{key}' nicht gefunden.")
        return

    # Kombiniere Root mit dem relativen Pfad zum File
    abs_path = ROOT_DIR / rel_path

    if not abs_path.exists():
        print(f"Fehler: Datei nicht gefunden unter {abs_path}")
        # Debug-Hilfe: Zeige an, wo wir gerade suchen
        print(f"ROOT_DIR wurde erkannt als: {ROOT_DIR}")
        return

    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            display(Markdown(f.read()))
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")