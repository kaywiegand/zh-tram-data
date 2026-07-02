"""
Ist-Daten → Parquet-Konverter (VBZ Tram Filter)

Verarbeitet alle ZIP-Archive und bereits entpackte Ordner in BASE_DIR:
- Filtert nur VBZ-Tram-Zeilen (BETREIBER_ID=85:3849, PRODUKT_ID=Tram)
- Speichert pro CSV eine .parquet-Datei in PARQUET_DIR
- Löscht jede CSV nach Verarbeitung
- ZIPs bleiben erhalten (Raw-Backup)
- Überspringt Parquets, die bereits existieren (Resume-fähig)
"""

import zipfile
import shutil
import subprocess
from pathlib import Path

import pandas as pd

# BASE_DIR zeigt auf den ursprünglichen Rohdaten-Ort (externe Platte, sf_data-research) —
# dort wurden die Original-ZIPs einmalig verarbeitet. Bereits fertige Parquets liegen unter
# PARQUET_DIR (zh-tram-data/data/interim/ist-daten) und wurden von dort übernommen.
BASE_DIR = Path("/Volumes/WGND13/sf_data-research/data/raw/ist-daten")
PARQUET_DIR = Path("~/Workspace/zh-tram-data/data/interim/ist-daten").expanduser()

FILTER_BETREIBER_ID = "85:3849"
FILTER_PRODUKT_ID = "Tram"

CSV_READ_KWARGS = dict(
    sep=";",
    encoding="utf-8",
    dtype=str,
    low_memory=False,
)


def process_csv(csv_path: Path) -> int:
    parquet_path = PARQUET_DIR / (csv_path.stem + ".parquet")

    if parquet_path.exists():
        print(f"  [skip] {csv_path.name} → parquet existiert bereits")
        csv_path.unlink()
        return -1

    try:
        df = pd.read_csv(csv_path, **CSV_READ_KWARGS)
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, **{**CSV_READ_KWARGS, "encoding": "latin-1"})

    mask = (df["BETREIBER_ID"] == FILTER_BETREIBER_ID) & (df["PRODUKT_ID"] == FILTER_PRODUKT_ID)
    df_filtered = df[mask]

    df_filtered.to_parquet(parquet_path, index=False, engine="pyarrow")
    rows = len(df_filtered)
    print(f"  [ok] {csv_path.name} → {rows:,} Zeilen → {parquet_path.name}")

    csv_path.unlink()
    return rows


def process_extracted_folder(folder: Path) -> None:
    all_csvs = sorted(folder.rglob("*.csv")) + sorted(folder.rglob("*.CSV"))
    # __MACOSX-Metadaten und macOS-Resource-Forks (._*.csv) ausschliessen
    csv_files = [
        f for f in all_csvs
        if "__MACOSX" not in f.parts and not f.name.startswith("._")
    ]
    if not csv_files:
        print(f"[info] Kein CSV in {folder.name} — Ordner wird gelöscht")
        shutil.rmtree(folder)
        return

    print(f"\n[Ordner] {folder.name} ({len(csv_files)} CSVs)")
    total = 0
    for csv in csv_files:
        n = process_csv(csv)
        if n > 0:
            total += n

    remaining = [
        f for f in list(folder.rglob("*.csv")) + list(folder.rglob("*.CSV"))
        if "__MACOSX" not in f.parts and not f.name.startswith("._")
    ]
    if not remaining:
        shutil.rmtree(folder)
        print(f"  [done] Ordner {folder.name} gelöscht")


def process_zip(zip_path: Path) -> None:
    folder_name = zip_path.stem
    extract_dir = BASE_DIR / folder_name

    print(f"\n[ZIP] {zip_path.name}")
    extract_dir.mkdir(exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
    except NotImplementedError:
        # Deflate64 — Python zipfile unterstützt das nicht, System-unzip verwenden
        subprocess.run(["unzip", "-q", "-o", str(zip_path), "-d", str(extract_dir)], check=True)

    process_extracted_folder(extract_dir)

    if extract_dir.exists():
        print(f"  [warn] Ordner {folder_name} noch vorhanden — bitte manuell prüfen")
    else:
        print(f"  [done] {zip_path.name} vollständig verarbeitet (ZIP bleibt erhalten)")


def main() -> None:
    PARQUET_DIR.mkdir(exist_ok=True)

    # 1. Bereits entpackte Ordner verarbeiten
    for folder in sorted(BASE_DIR.iterdir()):
        if folder.is_dir() and folder.name not in ("parquets",):
            process_extracted_folder(folder)

    # 2. ZIP-Archive verarbeiten
    for zip_path in sorted(BASE_DIR.glob("*.zip")):
        process_zip(zip_path)

    print("\n✓ Fertig.")


if __name__ == "__main__":
    main()
