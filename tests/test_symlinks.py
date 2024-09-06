import os
import pytest
from pathlib import Path

def test_simple_symlink(tmp_path):
    target = tmp_path / "target"
    symlink = tmp_path / "symlink"
    
    # Create a target file
    target.write_text("This is the target file.")
    
    # Create a symlink pointing to the target file
    symlink.symlink_to(target)
    
    # Verify the symlink points to the correct target
    assert symlink.is_symlink()
    assert symlink.resolve() == target
    assert symlink.read_text() == "This is the target file."

def test_symlink_loop(tmp_path):
    link1 = tmp_path / "link1"
    link2 = tmp_path / "link2"
    
    # Create a symlink loop
    link1.symlink_to(link2)
    link2.symlink_to(link1)
    
    # Verify the symlink loop
    assert link1.is_symlink()
    assert link2.is_symlink()
    with pytest.raises(OSError):
        link1.resolve()

def test_nested_symlinks(tmp_path):
    target = tmp_path / "target"
    symlink1 = tmp_path / "symlink1"
    symlink2 = tmp_path / "symlink2"
    
    # Create a target file
    target.write_text("This is the target file.")
    
    # Create nested symlinks
    symlink1.symlink_to(target)
    symlink2.symlink_to(symlink1)
    
    # Verify the nested symlinks
    assert symlink1.is_symlink()
    assert symlink2.is_symlink()
    assert symlink2.resolve() == target
    assert symlink2.read_text() == "This is the target file."