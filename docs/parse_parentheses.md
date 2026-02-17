Parse a string into a list.  The list contains the string between each pair of parentheses.  
If there is no string between a pair of parentheses, the list contains an empty string.
Add an element for each pair of parentheses, even when there's no text before the first opening parenthesis or 
after the last closing parenthesis.

For each opening parenthesis, ensure a corresponding entry in the result list
When we find an opening parenthesis, we always add the text before it to the result (even if it's an empty string)

After processing all parentheses, if there's remaining text (text after the last closing parenthesis), we add it.

Return the string if there are no parentheses.


Write a single function to perform the task.

Function signature:

```python
def parse_parentheses(string: str, open_parentheses: str="{{", close_parentheses: str="}}") -> list.
```

Safely assume that the input string is valid.  That is:

- Parentheses are matched. 
- Parentheses cannot be nested.
- open_parentheses and close_parentheses are different.
- The last characer of open_parentheses cannot be the same as the first character of close_parentheses.

Do not test for invalid input.

## Write pytest to verify the functionality.

Minimum valid test cases:  

parse_parentheses("A") == ["A"]  
parse_parentheses("A{{B}}C") == ["A", "B", "C"]
parse_parentheses("{{B}}C") == ["", "B", "C"]
parse_parentheses("{{B}}") == ["", "B", ""]
parse_parentheses("A{{B}}C{{D}}E") == ["A", "B", "C", "D", "E"]
parse_parentheses("A{{B}}{{D}}E") == ["A", "B", "", "D", "E"]
parse_parentheses("A{{}}C{{}}") == ["A", "", "C", "", ""]