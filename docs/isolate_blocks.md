## Write a single function to perform the task.

Check in this order:

1. The number of items in the list is in {1, 5, 9, ...}.  That is, len(list) = n * 4 + 1 for some n.
   - Raise a Value error "Invalid blocks" if the number of items in the list is not one of the above. 
2. Ensure that all items in the list are strings.
   - Raise a Value error "Invalid items"

Function signature:

```python
def isolate_blocks(list) -> list
```

Return the list with: 
- The first item [1]
- Items [1,[2,3,4]],5], that is the first item followed by list of three items,  followed by the next item.  
- Items [1,[2,3,4],5,[6,7,8]],9], that is the first item followed by a group of three item, followed by the next item and then the next group of three items.  

So, as len(list) = n * 4 + 1 for some n. There will be n groups of three items.

## Write pytest to verify the functionality.

Pytests should be in a separate file.

Minimum valid test cases:  

`isolate_blocks(["A"])` Returns `["A"]`
`isolate_blocks(["A","B","C","D""E"])` Returns ["A",["B","C","D"],"E"] 
`isolate_blocks(["A","B","C","D""E","F","G","H","I"])`  Returns ["A",["B","C","D"],"E",["F","G","H"],"I"] 

A ValueError shall be raised in these cases:

`isolate_blocks(["A","B"])`
`isolate_blocks([5])`