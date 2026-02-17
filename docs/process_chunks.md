## Write a single function to perform the task.

Function signature:

```python
def process_chunks(x: list[str]) -> list[str]
```

Action:

The argument is list with items of type string or type list.

Iterate through the list processing the items with type list.  We refer to these items as sub-lists.  Items of type string are passed through to the 

output list unchanged.

Each sub-list will have three elements of type string. 

Check in this order:

1. Raise a ValueError if the number of items in a sub-list is not 3 with message "Invalid sub-list length".
2. Raise a ValueError if list items are neither strings or lists with message "Invalid item type"
3. Raise a ValueError if the sub-list items are not all of type string with message "Invalid list item".

Let `[[x,y,z]]` represent the sub-list.

Parse the first and third strings, x and z, as a JSON, to produce python dictionaries.
Replace x and z with the dictionaries.

- Raise a ValueError if the parsing the json fails with message "Failed to parse JSON".

Output the original list with the first and last item of each sub-list converted to 
a python dictionary.

## Write pytest to verify the functionality.

Pytests should be in a separate file.

assert process_chunks(['A'])==['A']

process_chunks([5]) raise ValueError Invalid item type

process_chunks([['A']]) raise ValueError Invalid sub-list length

process_chunks([[5]]) raise ValueError Invalid list item

process_chunks([['A','B','C']]) raise ValueError Failed to parse json

process_chunks([["""

{  "name": "John Doe",  "email": "john@example.com",  "age": 30,  "active": true,  "roles": ["admin", "user"],  "address": {    "street": "123 Main St",    "city": "New York",    "country": "USA"  },  "projects": [    {"id": 1, "name": "Website Redesign"},    {"id": 2, "name": "Mobile App"}  ] }

""","B","""

{  "title": "John Doe" }

"""]]) succeeds because both the first and third items in the sub-list are valid json strings.

The function returns 

[{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "active": True,
    "roles": ["admin", "user"],
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "country": "USA"
    },
    "projects": [
        {"id": 1, "name": "Website Redesign"},
        {"id": 2, "name": "Mobile App"}
    ]
},"B",{"title": "John Doe"}]
