from typing import Optional  # Added 'Optional'
from typing import List

from typing_extensions import override

from mentat.auto_completer import get_command_filename_completions
from mentat.command.command import Command, CommandArgument
from mentat.session_context import SESSION_CONTEXT
from mentat.utils import get_relative_path


class IncludeCommand(Command, command_name="include"):
    @override
    async def apply(
        self, *args: str, external: Optional[bool] = False
    ) -> None:  # Modified signature
        session_context = SESSION_CONTEXT.get()
        stream = session_context.stream
        code_context = session_context.code_context

        if len(args) == 0:
            stream.send("No files specified", style="warning")
            return
        for file_path in args:
            included_paths = code_context.include(
                file_path, external=external
            )  # Passed 'external' flag
            for included_path in included_paths:
                rel_path = get_relative_path(included_path, session_context.cwd)
                stream.send(
                    f"{rel_path} added to context{' (external)' if external else ''}",
                    style="success",
                )

    @override
    @classmethod
    def arguments(cls) -> List[CommandArgument]:
        return [
            CommandArgument("required", ["path", "glob pattern"], repeatable=True),
            CommandArgument(
                "optional",
                "--external",
                action="store_true",
                help="Mark the included paths as external libraries",
            ),
        ]

    @override
    @classmethod
    def argument_autocompletions(
        cls, arguments: list[str], argument_position: int
    ) -> list[str]:
        return get_command_filename_completions(arguments[-1])

    @override
    @classmethod
    def help_message(cls) -> str:
        return "Add files to context. Use --external to include external library paths."
