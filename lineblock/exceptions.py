

class NestedExtractBeginMarkerError(Exception):
    """Exception raised when consecutive block begin markers are found without an end marker between them."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Nested block begin marker at line {line_number} "
                   f"in file '{source_file}'. "
                   f"Missing block end marker.")
        super().__init__(message)


class UnclosedBlockError(Exception):
    """Exception raised when a block extract marker is found without a corresponding end marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Unclosed block starting at line {line_number} "
                   f"in file '{source_file}'. "
                   f"Expected block end marker.")
        super().__init__(message)


class OrphanedExtractEndMarkerError(Exception):
    """Exception raised when a block end marker is found without a corresponding start marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Orphaned block end marker at line {line_number} "
                   f"in file '{source_file}'. "
                   f"No corresponding block extract marker found.")
        super().__init__(message)

class OrphanedInsertEndMarkerError(Exception):
    """Exception raised when a block end marker is found without a corresponding start marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Orphaned block end marker at line {line_number} "
                   f"in file '{source_file}'. "
                   f"No corresponding block insert marker found.")
        super().__init__(message)

class IncompatibleOptionsError(Exception):
    """Raised when incompatible options are provided."""
    pass


class NotAFileError(Exception):
    """Raised when a file is expected but not found."""
    pass
