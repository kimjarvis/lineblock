from lineblock.source import Source
from pathlib import Path
from lineblock.markers import Markers

def process(file_path: Path):
    print(f"Processing {type(file_path)} {file_path}")
    for markers in Markers.markers():
        s = Source(path=file_path, markers=markers).process_file()