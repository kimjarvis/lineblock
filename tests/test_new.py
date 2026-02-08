import pytest
from pathlib import Path
import tempfile

from lineblock.exceptions import OrphanedInsertEndMarkerError, OrphanedExtractEndMarkerError, UnclosedBlockError, NotAFileError, IncompatibleOptionsError
from lineblock.lineblock import lineblock

def test_basic():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """
        
<!-- block extract "basic" 0 0 0-->
line 1
line 2
line 3
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert(result==0)
        new_content = original_file.read_text()
        expected_content="""

<!-- block extract "basic" 0 0 0-->
line 1
line 2
line 3
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->
    line 1
    line 2
    line 3
    <!-- end insert -->

        """
        assert(new_content.replace('\r\n', '\n').strip()==expected_content.replace('\r\n', '\n').strip())


def test_idempotent():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "basic" 0 0 0-->
line 1
line 2
line 3
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->
    line 1
    line 2
    line 3
    <!-- end insert -->

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

<!-- block extract "basic" 0 0 0-->
line 1
line 2
line 3
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->
    line 1
    line 2
    line 3
    <!-- end insert -->

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_indent():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

    <!-- block extract "basic" -4 0 0-->
    line 1
    line 2
    line 3
    <!-- end extract -->

    <!-- block insert "basic" 8 0 0 -->
    
        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content="""

    <!-- block extract "basic" -4 0 0-->
    line 1
    line 2
    line 3
    <!-- end extract -->

    <!-- block insert "basic" 8 0 0 -->
                line 1
                line 2
                line 3
    <!-- end insert -->
    
        """
        assert(new_content.replace('\r\n', '\n').strip()==expected_content.replace('\r\n', '\n').strip())


def test_head_tail():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "basic" 0 0 0-->
line 1
line 2
line 3
<!-- end extract -->

    <!-- block insert "basic" 0 2 2 -->
    line a
    line b
    line c
    line d

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

<!-- block extract "basic" 0 0 0-->
line 1
line 2
line 3
<!-- end extract -->

    <!-- block insert "basic" 0 2 2 -->
    line a
    line b
    line 1
    line 2
    line 3
    line c
    line d
    <!-- end insert -->

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_identities():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "block A" 0 0 0-->
line A
<!-- end extract -->
<!-- block extract blockB 0 0 0-->
line B
<!-- end extract -->

    <!-- block insert "block A" 0 0 0 -->
    <!-- block insert blockB 0 0 0 -->
    
        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        print(new_content)
        expected_content = """

<!-- block extract "block A" 0 0 0-->
line A
<!-- end extract -->
<!-- block extract blockB 0 0 0-->
line B
<!-- end extract -->

    <!-- block insert "block A" 0 0 0 -->
    line A
    <!-- end insert -->
    <!-- block insert blockB 0 0 0 -->
    line B
    <!-- end insert -->
    
        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_unclosed_block_extract():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "basic" 0 0 0-->

        """
        original_file.write_text(original_content)
        with pytest.raises(UnclosedBlockError):
            lineblock(tmp_dir)

def test_orphaned_extract_end_maker():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- end extract -->

        """
        original_file.write_text(original_content)
        with pytest.raises(OrphanedExtractEndMarkerError):
            lineblock(tmp_dir)


def test_orphaned_insert_end_maker():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- end insert -->

        """
        original_file.write_text(original_content)
        with pytest.raises(OrphanedInsertEndMarkerError):
            lineblock(tmp_dir)


def test_eof():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "basic" 0 0 0-->
line 1
<!-- end extract -->
<!-- block insert "basic" 0 0 0 -->"""
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()+"<"
        expected_content = """
        
<!-- block extract "basic" 0 0 0-->
line 1
<!-- end extract -->
<!-- block insert "basic" 0 0 0 -->
line 1
<!-- end insert --><"""
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_empty_block():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "basic" 0 0 0-->
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """
        
<!-- block extract "basic" 0 0 0-->
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->
    <!-- end insert -->        
        
        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())

def test_empty_block_idempotent():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "basic" 0 0 0-->
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->
    <!-- end insert -->

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

<!-- block extract "basic" 0 0 0-->
<!-- end extract -->

    <!-- block insert "basic" 0 0 0 -->
    <!-- end insert -->        

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())

# todo: this should produce an error on the second block extract marker
def test_nesting():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

<!-- block extract "outer" 0 0 0-->
    <!-- block extract "inner" 0 0 0-->
    <!-- end extract -->
<!-- end extract -->

        """
        original_file.write_text(original_content)
        with pytest.raises(OrphanedExtractEndMarkerError):
            lineblock(tmp_dir)


def test_minimal():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """
        <!-- block extract "basic" 0 0 0-->
            line 1
        <!-- end extract -->
        <!-- block insert "basic" -16 0 0 -->
        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """
        <!-- block extract "basic" 0 0 0-->
            line 1
        <!-- end extract -->
        <!-- block insert "basic" -16 0 0 -->
            line 1
        <!-- end insert -->        
        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_individual_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """
        <!-- block extract "basic" 0 0 0-->
            line 1
        <!-- end extract -->
        <!-- block insert "basic" -16 0 0 -->
        """
        original_file.write_text(original_content)
        result = lineblock(original_file)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """
        <!-- block extract "basic" 0 0 0-->
            line 1
        <!-- end extract -->
        <!-- block insert "basic" -16 0 0 -->
            line 1
        <!-- end insert -->        
        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_python():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

# block extract "basic" 0 0 0
line 1
line 2
line 3
# end extract

    # block insert "basic" 0 0 0 

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

# block extract "basic" 0 0 0
line 1
line 2
line 3
# end extract

    # block insert "basic" 0 0 0 
    line 1
    line 2
    line 3
    # end insert

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())

def test_c():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

// block extract "basic" 0 0 0
line 1
line 2
line 3
// end extract

    // block insert "basic" 0 0 0 

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

// block extract "basic" 0 0 0
line 1
line 2
line 3
// end extract

    // block insert "basic" 0 0 0 
    line 1
    line 2
    line 3
    // end insert

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())

def test_assembly():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

; block extract "basic" 0 0 0
line 1
line 2
line 3
; end extract

    ; block insert "basic" 0 0 0 

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

; block extract "basic" 0 0 0
line 1
line 2
line 3
; end extract

    ; block insert "basic" 0 0 0 
    line 1
    line 2
    line 3
    ; end insert

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())

def test_SQL():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

-- block extract "basic" 0 0 0
line 1
line 2
line 3
-- end extract

    -- block insert "basic" 0 0 0 

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

-- block extract "basic" 0 0 0
line 1
line 2
line 3
-- end extract

    -- block insert "basic" 0 0 0 
    line 1
    line 2
    line 3
    -- end insert

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_c_multi_line():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

/* block extract "basic" 0 0 0*/
line 1
line 2
line 3
/* end extract */

    /* block insert "basic" 0 0 0 */

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

/* block extract "basic" 0 0 0*/
line 1
line 2
line 3
/* end extract */

    /* block insert "basic" 0 0 0 */
    line 1
    line 2
    line 3
    /* end insert */

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())


def test_ruby():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_file = Path(tmp_dir) / "basic.md"
        original_content = """

=begin block extract "basic" 0 0 0=end
line 1
line 2
line 3
=begin end extract =end

    =begin block insert "basic" 0 0 0 =end

        """
        original_file.write_text(original_content)
        result = lineblock(tmp_dir)
        assert (result == 0)
        new_content = original_file.read_text()
        expected_content = """

=begin block extract "basic" 0 0 0=end
line 1
line 2
line 3
=begin end extract =end

    =begin block insert "basic" 0 0 0 =end
    line 1
    line 2
    line 3
    =begin end insert =end

        """
        assert (new_content.replace('\r\n', '\n').strip() == expected_content.replace('\r\n', '\n').strip())
