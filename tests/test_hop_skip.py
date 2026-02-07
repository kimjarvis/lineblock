#!/usr/bin/env python3
"""Test script to verify hop and skip functionality"""

from pathlib import Path
import tempfile
import os
from lineblock.block_insert import block_insert

def test_hop_skip_functionality():
    """Test the hop and skip functionality as described in the problem statement"""
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create the block file to be inserted
        block_file = Path(tmp_dir) / "examples" / "factorial_example.md"
        block_file.parent.mkdir(parents=True, exist_ok=True)
        
        factorial_content = """def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)"""
        
        block_file.write_text(factorial_content)
        
        # Create the source file with hop=1 and skip=1
        source_file = Path(tmp_dir) / "factorial.md"
        source_content = """<!-- block insert examples/factorial_example.md 0 1 1-->
line 1
line 2
line 3"""
        source_file.write_text(source_content)
        
        # Create output directory
        output_dir = Path(tmp_dir) / "output"
        output_dir.mkdir()
        
        # Run block insert
        block_insert(
            source_file=str(source_file),
            insert_directory_prefix=tmp_dir,
            output_directory=str(output_dir)
        )
        
        # Check the output
        output_file = output_dir / "factorial.md"
        result = output_file.read_text()
        
        expected_result = """<!-- block insert examples/factorial_example.md 0 1 1-->
line 1
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
line 2
<!-- end insert -->
line 3"""
        
        print("Input:")
        print(source_content)
        print("\nActual output:")
        print(result)
        print("\nExpected output:")
        print(expected_result)
        
        # Normalize whitespace for comparison
        result_normalized = result.replace('\r\n', '\n').strip()
        expected_normalized = expected_result.replace('\r\n', '\n').strip()
        
        if result_normalized == expected_normalized:
            print("\n✓ Hop and skip functionality works correctly!")
        else:
            print("\n✗ Hop and skip functionality failed!")
            print("Difference found:")
            print(f"Expected: {repr(expected_normalized)}")
            print(f"Got: {repr(result_normalized)}")

def test_hop_only():
    """Test hop functionality only (skip=0)"""
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create the block file to be inserted
        block_file = Path(tmp_dir) / "examples" / "factorial_example.md"
        block_file.parent.mkdir(parents=True, exist_ok=True)
        
        factorial_content = """def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)"""
        
        block_file.write_text(factorial_content)
        
        # Create the source file with hop=1 and skip=0
        source_file = Path(tmp_dir) / "factorial.md"
        source_content = """<!-- block insert examples/factorial_example.md 0 1 0 -->
line 1
line 2
line 3"""
        source_file.write_text(source_content)
        
        # Create output directory
        output_dir = Path(tmp_dir) / "output"
        output_dir.mkdir()
        
        # Run block insert
        block_insert(
            source_file=str(source_file),
            insert_directory_prefix=tmp_dir,
            output_directory=str(output_dir)
        )
        
        # Check the output
        output_file = output_dir / "factorial.md"
        result = output_file.read_text()
        
        expected_result = """<!-- block insert examples/factorial_example.md 0 1 0 -->
line 1
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
<!-- end insert -->
line 2
line 3"""
        
        print("\nTest hop only (hop=1, skip=0):")
        print("Input:")
        print(source_content)
        print("\nActual output:")
        print(result)
        print("\nExpected output:")
        print(expected_result)
        
        # Normalize whitespace for comparison
        result_normalized = result.replace('\r\n', '\n').strip()
        expected_normalized = expected_result.replace('\r\n', '\n').strip()
        
        if result_normalized == expected_normalized:
            print("\n✓ Hop only functionality works correctly!")
        else:
            print("\n✗ Hop only functionality failed!")
            print("Difference found:")
            print(f"Expected: {repr(expected_normalized)}")
            print(f"Got: {repr(result_normalized)}")

def test_skip_only():
    """Test skip functionality only (hop=0)"""
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create the block file to be inserted
        block_file = Path(tmp_dir) / "examples" / "factorial_example.md"
        block_file.parent.mkdir(parents=True, exist_ok=True)
        
        factorial_content = """def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)"""
        
        block_file.write_text(factorial_content)
        
        # Create the source file with hop=0 and skip=1
        source_file = Path(tmp_dir) / "factorial.md"
        source_content = """<!-- block insert examples/factorial_example.md 0 0 1 -->
line 1
line 2
line 3"""
        source_file.write_text(source_content)
        
        # Create output directory
        output_dir = Path(tmp_dir) / "output"
        output_dir.mkdir()
        
        # Run block insert
        block_insert(
            source_file=str(source_file),
            insert_directory_prefix=tmp_dir,
            output_directory=str(output_dir)
        )
        
        # Check the output
        output_file = output_dir / "factorial.md"
        result = output_file.read_text()
        
        expected_result = """<!-- block insert examples/factorial_example.md 0 0 1 -->
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
line 1
<!-- end insert -->
line 2
line 3"""
        
        print("\nTest skip only (hop=0, skip=1):")
        print("Input:")
        print(source_content)
        print("\nActual output:")
        print(result)
        print("\nExpected output:")
        print(expected_result)
        
        # Normalize whitespace for comparison
        result_normalized = result.replace('\r\n', '\n').strip()
        expected_normalized = expected_result.replace('\r\n', '\n').strip()
        
        if result_normalized == expected_normalized:
            print("\n✓ Skip only functionality works correctly!")
        else:
            print("\n✗ Skip only functionality failed!")
            print("Difference found:")
            print(f"Expected: {repr(expected_normalized)}")
            print(f"Got: {repr(result_normalized)}")

if __name__ == "__main__":
    test_hop_skip_functionality()
    test_hop_only()
    test_skip_only()