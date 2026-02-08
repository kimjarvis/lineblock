from lineblock.source import Source
from lineblock.sink import Sink
from pathlib import Path
from lineblock.markers import Markers

def process(root_path: Path = None, file_path: Path = None):
    block_map = []
    for markers in Markers.markers():
        s = Source(path=file_path, markers=markers)
        s.process_file()
        block_map.extend(s.block_map)
    return block_map


def process_inserts(block_map: dict = None, file_path: Path = None):
    for markers in Markers.markers():
        s = Sink(source_file=file_path, markers=markers,block_map=block_map)
        s.process_file()
