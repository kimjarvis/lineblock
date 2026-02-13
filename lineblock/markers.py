class Markers:
    """
    Default values for command line parameters.
    """

    _data = [
        {
            "type": "HTML",
            "Extract": {
                "Begin": r'(\s*)<!--\s*block extract\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*-->.*',
                "End": r"<!--\s*end extract.*?\s*-->.*",
            },
            "Insert": {
                "Begin": r'(\s*)<!--\s*block insert\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*-->.*',
                "End": r"<!--\s*end insert.*?\s*-->.*",
                "Marker": r"<!-- end insert -->",
            },
        },
        {
            "type": "Python",
            "Extract": {
                "Begin": r'(\s*)#\s*block extract\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r"#\s*end extract.*?\s*.*",
            },
            "Insert": {
                "Begin": r'(\s*)#\s*block insert\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r"#\s*end insert.*?\s*.*",
                "Marker": r"# end insert",
            },
        },
        {
            "type": "C",
            "Extract": {
                "Begin": r'(\s*)//\s*block extract\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r"//\s*end extract.*?\s*.*",
            },
            "Insert": {
                "Begin": r'(\s*)//\s*block insert\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r"//\s*end insert.*?\s*.*",
                "Marker": r"// end insert",
            },
        },
        {
            "type": "Assembly",
            "Extract": {
                "Begin": r'(\s*);\s*block extract\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r";\s*end extract.*?\s*.*",
            },
            "Insert": {
                "Begin": r'(\s*);\s*block insert\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r";\s*end insert.*?\s*.*",
                "Marker": r"; end insert",
            },
        },
        {
            "type": "SQL",
            "Extract": {
                "Begin": r'(\s*)--\s*block extract\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r"--\s*end extract.*?\s*.*",
            },
            "Insert": {
                "Begin": r'(\s*)--\s*block insert\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*',
                "End": r"--\s*end insert.*?\s*.*",
                "Marker": r"-- end insert",
            },
        },
        {
            "type": "C Multi-Line",
            "Extract": {
                "Begin": r'(\s*)/\*\s*block extract\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*\*/.*',
                "End": r"/\*\s*end extract.*?\s*\*/.*",
            },
            "Insert": {
                "Begin": r'(\s*)/\*\s*block insert\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*\*/.*',
                "End": r"/\*\s*end insert.*?\s*\*/.*",
                "Marker": r"/* end insert */",
            },
        },
        {
            "type": "Ruby",
            "Extract": {
                "Begin": r'(\s*)=begin\s*block extract\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*=end.*',
                "End": r"=begin\s*end extract.*?\s*=end.*",
            },
            "Insert": {
                "Begin": r'(\s*)=begin\s*block insert\s+(?:"([^"]*)"|\'([^\']*)\'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*=end.*',
                "End": r"=begin\s*end insert.*?\s*=end.*",
                "Marker": r"=begin end insert =end",
            },
        },
        {
            "type": "Visual Basic",
            "Extract": {
                "Begin": r"(\s*)'\s*block extract\s+(?:\"([^\"]*)\"|'([^']*)'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*",
                "End": r"'\s*end extract.*?\s*.*",
            },
            "Insert": {
                "Begin": r"(\s*)'\s*block insert\s+(?:\"([^\"]*)\"|'([^']*)'|(\S+))(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*.*",
                "End": r"'\s*end insert.*?\s*.*",
                "Marker": r"' end insert",
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
