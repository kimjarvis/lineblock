# Lineblocks

Lineblocks is a documentation synchronization tool that maintains consistency between code examples and their corresponding documentation.

Primary Use Case: Keeping Code Documentation Up to Date

The tool addresses the common problem where documentation becomes outdated as code evolves. Developers often copy-paste code examples into documentation, but when the source code changes, these examples quickly become inaccurate. This program solves this by:

- Single Source of Truth: Code examples are stored in actual source files, not duplicated in documentation

- Automatic Synchronization: Running this program updates all documentation with the latest code examples

- Consistent Formatting: Maintains proper indentation and structure when inserting code blocks

- Error Detection: Identifies orphaned markers and missing files to prevent broken documentation

# Installation 

```bash
pipx install lineblock
```
# Usage

Add markers to the source code

```python
def test_lineblocks():
    # block extract test.txt
    import lineblock
    lineblock.lineblocks("extract", source="README.md", prefix=".")
    lineblock.lineblocks("insert", source=".", prefix=".")
    # end extract
```

In your documentation, add markers to indicate where code examples should be inserted.

%% markdown %%

```python
%% markdown %%
```


```python
<!-- block insert test.txt -->
        """Test when a block extract marker has no corresponding end marker."""
        source_path = "tests/sources/extract_orphaned_begin_marker.md"
    
        with pytest.raises(UnclosedBlockError) as exc_info:
            block_extract(
                source_path="tests/sources/extract_orphaned_begin_marker.md",
                extract_directory_prefix="tests/snippets"
            )
    
        assert "Unclosed block" in str(exc_info.value)
        assert "extract_orphaned_begin_marker.md" in str(exc_info.value)
        assert "Expected end marker" in str(exc_info.value)
<!-- end insert -->
```

Run the extraction process to create the file test.txt

```bash
lineblock extract --source=README.md --prefix=.
```

Run the insertion process to insert the code examples into your documentation.

```bash
lineblock insert --source=. --prefix=.
```


