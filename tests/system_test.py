import os
import tempfile
from pathlib import Path
from textwrap import dedent

import pytest
from mentat.include_files import get_paths_for_directory

from mentat.session import Session
from tests.conftest import run_git_command


def test_system():
    # Create a temporary file
    temp_file_name = Path("temp.py")
    with open(temp_file_name, "w") as f:
        f.write("# This is a temporary file.")
    mock_collect_user_input.set_stream_messages(
        [
            "Add changes to the file",
            "i",
            "y",
            "q",
        ]
    )

    mock_call_llm_api.set_streamed_values([dedent("""\
        I will add a print statement.

        Steps:
        1. Add a print statement after the last line

        @@start
        {{
            "file": "{file_name}",
            "action": "replace",
            "start-line": 1,
            "end-line": 1
        }}
        @@code
        print("Hello, world!")
        @@end""".format(file_name=temp_file_name))])

    session = Session(cwd=Path.cwd(), paths=[temp_file_name])
    session.start()
    session.stream.recv(channel="client_exit")

    # Check if the temporary file is modified as expected
    with open(temp_file_name, "r") as f:
        content = f.read()
        expected_content = 'print("Hello, world!")'
    assert content == expected_content


def test_system_exits_on_exception():
    # if we don't catch this and shutdown properly, pytest will fail test
    # with "Task was destroyed but it is pending!"
    mock_collect_user_input.side_effect = [Exception("Something went wrong")]

    session = Session(cwd=Path.cwd())
    session.start()
    session.stream.recv(channel="session_stopped")


def test_interactive_change_selection():
    # Create a temporary file
    temp_file_name = Path("temp_interactive.py")
    with open(temp_file_name, "w") as f:
        f.write("# This is a temporary file for interactive test.")
    mock_collect_user_input.set_stream_messages(
        [
            "Add changes to the file",
            "i",
            "y",
            "n",
            "y",
            "q",
        ]
    )

    mock_call_llm_api.set_streamed_values([dedent("""\
        I will make three changes to the file.

        Steps:
        1. Replace the comment with print("Change 1")
        2. Add print("Change 2") after the first line
        3. Add print("Change 3") after the second line

        @@start
        {{
            "file": "{file_name}",
            "action": "replace",
            "start-line": 1,
            "end-line": 1
        }}
        @@code
        print("Change 1")
        @@end
        @@start
        {{
            "file": "{file_name}",
            "action": "insert",
            "insert-after-line": 1,
            "insert-before-line": 2
        }}
        @@code
        print("Change 2")
        @@end
        @@start
        {{
            "file": "{file_name}",
            "action": "insert",
            "insert-after-line": 2,
            "insert-before-line": 3
        }}
        @@code
        print("Change 3")
        @@end""".format(file_name=temp_file_name))])

    session = Session(cwd=Path.cwd(), paths=[temp_file_name])
    session.start()
    session.stream.recv(channel="client_exit")

    # Check if the temporary file is modified as expected
    with open(temp_file_name, "r") as f:
        content = f.read()
        expected_content = 'print("Change 1")\n\nprint("Change 3")'

    assert content == expected_content


# Makes sure we're properly turning the model output into correct path no matter the os
def test_without_os_join():
    temp_dir = "dir"
    temp_file_name = "temp.py"
    temp_file_path = Path(os.path.join(temp_dir, temp_file_name))
    os.makedirs(temp_dir, exist_ok=True)
    with open(temp_file_path, "w") as f:
        f.write("# This is a temporary file.")

    mock_collect_user_input.set_stream_messages(
        ['Replace comment with print("Hello, world!")', "y", "q"]
    )

    # Use / here since that should always be what the model outputs
    fake_file_path = temp_dir + "/" + temp_file_name
    mock_call_llm_api.set_streamed_values([dedent("""\
        I will add a print statement.
        Steps:
        1. Add a print statement after the last line
        @@start
        {{
            "file": "{file_name}",
            "action": "replace",
            "start-line": 1,
            "end-line": 1
        }}
        @@code
        print("Hello, world!")
        @@end""".format(file_name=fake_file_path))])
    session = Session(cwd=Path.cwd(), paths=[temp_file_path])
    session.start()
    session.stream.recv(channel="client_exit")
    mock_collect_user_input.reset_mock()
    with open(temp_file_path, "r") as f:
        content = f.read()
        expected_content = 'print("Hello, world!")'
    assert content == expected_content


def test_sub_directory(temp_testbed, monkeypatch):
    with monkeypatch.context() as m:
        m.chdir("scripts")
        file_name = "calculator.py"
        mock_collect_user_input.set_stream_messages(
            [
                "Add changes to the file",
                "y",
                "q",
            ]
        )

        mock_call_llm_api.set_streamed_values([dedent(f"""\
            Conversation

            @@start
            {{
                "file": "scripts/{file_name}",
                "action": "replace",
                "start-line": 1,
                "end-line": 50
            }}
            @@code
            print("Hello, world!")
            @@end""")])

        session = Session(cwd=temp_testbed, paths=[Path("scripts", file_name)])
        session.start()
        session.stream.recv(channel="client_exit")

        # Check if the temporary file is modified as expected
        with open(file_name, "r") as f:
            content = f.read()
            expected_content = 'print("Hello, world!")'
        assert content == expected_content


@pytest.mark.no_git_testbed
@pytest.mark.clear_testbed
def test_recursive_git_repositories(temp_testbed):
    # Tests if a git repo inside of a git repo inside of a git repo works, from outside of a git repo

    dirs = ["outer", "git1", "git2", "inner1", "git3", "inner2"]
    total_path = Path(".")
    files = []
    for dir_name in dirs:
        file_path = total_path / (dir_name + ".txt")
        with open(file_path, "w") as f:
            f.write("")
        files.append(temp_testbed / file_path)

        total_path = total_path / dir_name
        os.mkdir(total_path)
        if dir_name.startswith("git"):
            run_git_command(total_path, "init")
    file_path = total_path / "innermost.txt"
    with open(file_path, "w") as f:
        f.write("")
    files.append(temp_testbed / file_path)

    mock_collect_user_input.set_stream_messages(
        [
            "q",
        ]
    )

    session = Session(cwd=temp_testbed, paths=[Path(".")])
    session.start()
    session.stream.recv(channel="client_exit")

    assert set(session.ctx.code_context.include_files.keys()) == set(files)


def test_symlink_handling():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        file_path = temp_dir_path / "file.txt"
        symlink_path = temp_dir_path / "symlink.txt"
        
        # Create a regular file
        with open(file_path, "w") as f:
            f.write("This is a test file.")
        
        # Create a symlink to the regular file
        os.symlink(file_path, symlink_path)
        
        # Test the function that should handle symlinks
        paths = get_paths_for_directory(temp_dir_path)
        
        # Assert that both the file and the symlink are included
        assert file_path.resolve() in paths
        assert symlink_path.resolve() in paths


def test_symlink_loop_handling():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        dir_path = temp_dir_path / "dir"
        symlink_path = dir_path / "symlink"
        
        # Create a directory
        os.mkdir(dir_path)
        
        # Create a symlink that points to its own parent directory (loop)
        os.symlink(dir_path, symlink_path)
        
        # Test the function that should handle symlinks
        paths = get_paths_for_directory(temp_dir_path)
        
        # Assert that the function does not enter an infinite loop
        assert dir_path.resolve() in paths
        assert symlink_path.resolve() not in paths  # Should not follow the loop
