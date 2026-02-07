class Markers:
    """
    Default values for command line parameters.
    """

    _data = [
        {
            "type": "Markdown",
            "Extract": {
                "Begin": r"(\s*)<!--\s*block extract\s+(\S+)(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*\s*-->.*",
                "End": r"<!--\s*end extract.*?\s*-->.*",
            },
            "Insert": {
                "Begin": r"<!--\s*block insert\s+(\S+)(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*\s*-->.*",
                "End": r"<!--\s*end insert.*?\s*-->.*",
                "Marker": r"<!-- end insert -->",
            },
        },
        {
            "type": "Python",
            "Extract": {
                "Begin": r"(\s*)#\s*block extract\s+(\S+)(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*\s*.*",
                "End": r"#\s*end extract.*?\s*.*",
            },
            "Insert": {
                "Begin": r"#\s*block insert\s+(\S+)(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*\s*.*",
                "End": r"#\s*end insert.*?\s*.*",
                "Marker": r"# end insert",
            },
        }
    ]

    @classmethod
    def markers(cls):
        """
        Generator that yields each marker configuration dictionary from _data.

        Yields:
            dict: The next marker configuration dictionary from the _data list
        """
        for marker_data in cls._data:
            yield marker_data
