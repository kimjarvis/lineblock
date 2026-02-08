from lineblock.source import Source
from pathlib import Path
from lineblock.markers import Markers

def process(root_path: Path = None, file_path: Path = None):
    print(f"Processing  {root_path} {file_path}")
    block_map = []
    for markers in Markers.markers():
        s = Source(path=file_path, markers=markers)
        s.process_file()
        block_map.extend(s.block_map)
    print(f"Block map:  {block_map}")
    return block_map