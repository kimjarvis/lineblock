"""
Lineblock package - Documentation synchronization tool.

This package provides functionality to maintain consistency between code examples 
and their corresponding documentation by inserting and extracting code blocks 
based on markers in files.
"""

from .block_extract import BlockExtract
from .block_insert import BlockInsert
from .exceptions import UnclosedBlockError, OrphanedExtractEndMarkerError

# Import main function for CLI usage
from .cli import main, lineblock

__version__ = "0.0.1"
__author__ = "Kim Jarvis"
__email__ = "kim.jarvis@tpfsystems.com"
__all__ = [
    'BlockExtract',
    'BlockInsert',
    'UnclosedBlockError',
    'OrphanedExtractEndMarkerError',
    'main',
    'lineblock'
]