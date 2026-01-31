class Common:

    @staticmethod
    def indent_lines(lines, spaces):
        indented = []
        for line in lines:
            stripped = line.rstrip("\n")
            if spaces >= 0:
                # Positive indent: add spaces
                indented_line = f"{' ' * spaces}{stripped}\n"
            else:
                # Negative indent: remove spaces from the beginning
                # Remove up to |spaces| spaces, but not beyond the first non-space character
                spaces_to_remove = -spaces
                # Count leading spaces in the original line
                leading_spaces = len(stripped) - len(stripped.lstrip())
                # Remove spaces, but not more than what exists
                remove_count = min(spaces_to_remove, leading_spaces)
                indented_line = stripped[remove_count:] + "\n"
            indented.append(indented_line)
        return indented
