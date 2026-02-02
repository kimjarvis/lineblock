class Defaults:
    """
    Default values for command line parameters.
    """
    _data = {
        "md": {
            "type": "Markdown",
            "Extract": {
                "Begin": {
                    "Prefix": "#\s*block extract\s+",
                    "Suffix": "",
                    "Marker": "<!-- block extract myblock.md -->",
                },
                "End": {
                    "Prefix": "#\s*end extract\s+",
                    "Suffix": "",
                    "Marker": "<!-- block extract end -->",
                }
            },
            "Insert": {
                "Begin": {
                    "Prefix": "<!--\s*block insert\s+",
                    "Suffix": "\s*-->",
                    "Marker": "<!-- block insert myblock.md -->",
                },
                "End": {
                    "Prefix": "<!--\s*end insert",
                    "Suffix": "\s*-->",
                    "Marker": "<!-- block insert end -->",
                }
            }
        }
    }

    def __class_getitem__(cls, key):
        return cls._data[key]


def main():
    # Verify the condition
    result = Defaults["md"]["Insert"]["Begin"]["Prefix"] == r"#\s*block extract\s+"
    print(result)  # Should print True


if __name__ == "__main__":
    main()
