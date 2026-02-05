class Defaults:
    """
    Default values for command line parameters.
    """
    _data = {
        "md": {
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
                }
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
                }
            }
        },
        "py": {
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
                }
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
                }
            }
        }

    }

    def __class_getitem__(cls, key):
        return cls._data[key]


def main():
    # Verify the condition
    result = Defaults["py"]["Extract"]["Begin"]["Prefix"] == r"#\s*block extract\s+"
    print(result)  # Should print True


if __name__ == "__main__":
    main()
