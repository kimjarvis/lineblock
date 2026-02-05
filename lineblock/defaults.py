class Defaults:
    """
    Default values for command line parameters.
    """

    _data = {
        ".md": {
            "type": "Markdown",
            "Extract": {
                "Begin": {
                    "Prefix": r"<!--\s*block extract\s",
                    "Suffix": r"",
                    "Marker": r"<!-- block extract <myblock.md> <n> <comment> -->",
                },
                "End": {
                    "Prefix": r"<!--\s*end extract\s",
                    "Suffix": r"",
                    "Marker": r"<!-- block extract end -->",
                },
            },
            "Insert": {
                "Begin": {
                    "Prefix": r"<!--\s*block insert\s+",
                    "Suffix": r"\s*-->",
                    "Marker": "<!-- block insert <myblock.md> -->",
                },
                "End": {
                    "Prefix": r"<!--\s*end insert",
                    "Suffix": r"\s*-->",
                    "Marker": r"<!-- block insert end -->",
                },
            },
        },
        ".py": {
            "type": "Python",
            "Extract": {
                "Begin": {
                    "Prefix": r"#\s*block extract\s+",
                    "Suffix": r"",
                    "Marker": r"# block extract <myblock.py> <n>-->",
                },
                "End": {
                    "Prefix": r"#\s*end extract\s+",
                    "Suffix": r"",
                    "Marker": r"# block extract end",
                },
            },
            "Insert": {
                "Begin": {
                    "Prefix": r"#\s*block insert\s",
                    "Suffix": r"",
                    "Marker": r"# block insert <myblock.md> -->",
                },
                "End": {
                    "Prefix": r"#\s*end insert\s",
                    "Suffix": r"",
                    "Marker": r"# block insert end",
                },
            },
        },
    }

    @classmethod
    def check_markers(cls, file_type):
        return True if file_type in cls._data else False

    @classmethod
    def get_markers(cls, file_type):
        """
        Retrieve markers for the specified file type.

        Args:
            file_type (str): The file type to retrieve markers for (e.g., ".md", ".py").

        Returns:
            dict: The dictionary of markers for the specified file type.

        Raises:
            ValueError: If the file_type is not found in the data.
        """
        if file_type not in cls._data:
            raise ValueError(f"File type '{file_type}' not found.")
        return cls._data[file_type]

    def __class_getitem__(cls, key):
        return cls._data[key]


def main():
    # Verify the condition
    result = Defaults[".py"]["Extract"]["Begin"]["Prefix"] == r"#\s*block extract\s+"
    print(result)  # Should print True

    # Test get_markers method
    try:
        md_markers = Defaults.get_markers(".md")
        print(md_markers)  # Should print the Markdown markers dictionary
        nonexistent_markers = Defaults.get_markers("nonexistent")
    except ValueError as e:
        print(e)  # Should print an error message for the nonexistent file type


if __name__ == "__main__":
    main()
