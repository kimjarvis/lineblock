class UnclosedBlockError(Exception):
    """Exception raised when a block extract marker is found without a corresponding end marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Unclosed block starting at line {line_number} "
                   f"in file '{source_file}'. "
                   f"Expected end marker '# block end' or '<!-- block end -->'.")
        super().__init__(message)


class OrphanedExtractEndMarkerError(Exception):
    """Exception raised when a block end marker is found without a corresponding start marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Orphaned block end marker at line {line_number} "
                   f"in file '{source_file}'. "
                   f"No corresponding '# block extract' or '<!-- block extract -->' marker found.")
        super().__init__(message)

class OrphanedInsertEndMarkerError(Exception):
    """Exception raised when a block end marker is found without a corresponding start marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Orphaned block end marker at line {line_number} "
                   f"in file '{source_file}'. "
                   f"No corresponding '# block insert' or '<!-- block insert -->' marker found.")
        super().__init__(message)
